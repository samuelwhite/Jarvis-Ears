#pragma once

#include "esphome/components/microphone/microphone.h"
#include "esphome/core/component.h"

#include <deque>
#include <mutex>
#include <string>
#include <vector>

namespace esphome {
namespace tcp_audio_emitter {

class TCPAudioEmitter : public Component {
 public:
  void set_microphone(microphone::Microphone *microphone) { this->microphone_ = microphone; }
  void set_host(const std::string &host) { this->host_ = host; }
  void set_port(uint16_t port) { this->port_ = port; }
  void set_auto_start(bool auto_start) { this->auto_start_ = auto_start; }

  void setup() override;
  void loop() override;
  void dump_config() override;

 protected:
  void handle_audio_(const std::vector<uint8_t> &data);
  bool connect_socket_();
  void disconnect_socket_();
  bool send_next_chunk_();

  microphone::Microphone *microphone_{nullptr};
  std::string host_{};
  uint16_t port_{8765};
  bool auto_start_{true};
  bool microphone_started_{false};
  int socket_fd_{-1};
  uint32_t last_connect_attempt_ms_{0};
  uint32_t dropped_chunks_{0};
  size_t queued_bytes_{0};
  std::mutex queue_mutex_{};
  std::deque<std::vector<uint8_t>> pending_chunks_{};

  static constexpr size_t MAX_QUEUE_BYTES = 32768;
  static constexpr uint32_t CONNECT_RETRY_MS = 1000;
};

}  // namespace tcp_audio_emitter
}  // namespace esphome
