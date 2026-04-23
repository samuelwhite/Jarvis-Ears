#include "tcp_audio_emitter.h"

#include "esphome/core/log.h"

#include <cerrno>
#include <cstring>

#include <lwip/inet.h>
#include <lwip/sockets.h>

namespace esphome {
namespace tcp_audio_emitter {

static const char *const TAG = "tcp_audio_emitter";

void TCPAudioEmitter::setup() {
  if (this->microphone_ == nullptr) {
    ESP_LOGE(TAG, "No microphone configured");
    this->mark_failed();
    return;
  }

  auto stream_info = this->microphone_->get_audio_stream_info();
  ESP_LOGI(TAG, "Experimental TCP emitter setup");
  ESP_LOGI(TAG, "Audio stream: %u Hz, %u channels, %u bits/sample", stream_info.get_sample_rate(),
           stream_info.get_channels(), stream_info.get_bits_per_sample());
  ESP_LOGW(TAG, "This component is an experiment only. It is not production ingest.");

  this->microphone_->add_data_callback(
      [this](const std::vector<uint8_t> &data) { this->handle_audio_(data); });

  if (this->auto_start_) {
    this->microphone_->start();
    this->microphone_started_ = true;
    ESP_LOGI(TAG, "Microphone capture started automatically");
  }
}

void TCPAudioEmitter::loop() {
  if (this->is_failed()) {
    return;
  }

  if (!this->microphone_started_ && this->auto_start_) {
    this->microphone_->start();
    this->microphone_started_ = true;
    ESP_LOGI(TAG, "Microphone capture started from loop");
  }

  if (this->socket_fd_ < 0) {
    const uint32_t now = millis();
    if (now - this->last_connect_attempt_ms_ >= CONNECT_RETRY_MS) {
      this->last_connect_attempt_ms_ = now;
      this->connect_socket_();
    }
    return;
  }

  if (!this->send_next_chunk_()) {
    this->disconnect_socket_();
  }
}

void TCPAudioEmitter::dump_config() {
  ESP_LOGCONFIG(TAG, "TCP Audio Emitter");
  ESP_LOGCONFIG(TAG, "  Host: %s", this->host_.c_str());
  ESP_LOGCONFIG(TAG, "  Port: %u", this->port_);
  ESP_LOGCONFIG(TAG, "  Auto Start: %s", YESNO(this->auto_start_));
  ESP_LOGCONFIG(TAG, "  Max Queue Bytes: %u", static_cast<unsigned>(MAX_QUEUE_BYTES));
}

void TCPAudioEmitter::handle_audio_(const std::vector<uint8_t> &data) {
  if (data.empty()) {
    return;
  }

  std::lock_guard<std::mutex> lock(this->queue_mutex_);
  if (this->queued_bytes_ + data.size() > MAX_QUEUE_BYTES) {
    this->dropped_chunks_++;
    if ((this->dropped_chunks_ % 25) == 1) {
      ESP_LOGW(TAG, "Dropping microphone chunk bytes=%u queued_bytes=%u dropped_chunks=%u",
               static_cast<unsigned>(data.size()), static_cast<unsigned>(this->queued_bytes_),
               static_cast<unsigned>(this->dropped_chunks_));
    }
    return;
  }

  this->pending_chunks_.push_back(data);
  this->queued_bytes_ += data.size();
}

bool TCPAudioEmitter::connect_socket_() {
  this->disconnect_socket_();

  const int socket_fd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
  if (socket_fd < 0) {
    ESP_LOGE(TAG, "socket() failed errno=%d", errno);
    return false;
  }

  sockaddr_in address {};
  address.sin_family = AF_INET;
  address.sin_port = htons(this->port_);
  const int parse_result = inet_pton(AF_INET, this->host_.c_str(), &address.sin_addr);
  if (parse_result != 1) {
    ESP_LOGE(TAG, "Host must be an IPv4 literal for this draft emitter: %s", this->host_.c_str());
    ::close(socket_fd);
    return false;
  }

  ESP_LOGI(TAG, "Connecting to collector %s:%u", this->host_.c_str(), this->port_);
  if (::connect(socket_fd, reinterpret_cast<sockaddr *>(&address), sizeof(address)) != 0) {
    ESP_LOGW(TAG, "connect() failed errno=%d", errno);
    ::close(socket_fd);
    return false;
  }

  this->socket_fd_ = socket_fd;
  ESP_LOGI(TAG, "Collector connected");
  return true;
}

void TCPAudioEmitter::disconnect_socket_() {
  if (this->socket_fd_ >= 0) {
    ::close(this->socket_fd_);
    this->socket_fd_ = -1;
    ESP_LOGW(TAG, "Collector socket closed");
  }
}

bool TCPAudioEmitter::send_next_chunk_() {
  std::vector<uint8_t> chunk;
  {
    std::lock_guard<std::mutex> lock(this->queue_mutex_);
    if (this->pending_chunks_.empty()) {
      return true;
    }
    chunk = std::move(this->pending_chunks_.front());
    this->pending_chunks_.pop_front();
    this->queued_bytes_ -= chunk.size();
  }

  size_t sent_total = 0;
  while (sent_total < chunk.size()) {
    const int sent = ::send(this->socket_fd_, chunk.data() + sent_total, chunk.size() - sent_total, 0);
    if (sent <= 0) {
      ESP_LOGW(TAG, "send() failed errno=%d while sending chunk bytes=%u", errno,
               static_cast<unsigned>(chunk.size()));
      return false;
    }
    sent_total += static_cast<size_t>(sent);
  }

  ESP_LOGD(TAG, "Sent chunk bytes=%u", static_cast<unsigned>(chunk.size()));
  return true;
}

}  // namespace tcp_audio_emitter
}  // namespace esphome
