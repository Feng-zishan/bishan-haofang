// 璧山好房 · 语音识别
// 基于 Web Speech API，支持微信浏览器

const VoiceInput = {
  recognition: null,
  isSupported: false,
  isListening: false,

  init() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'zh-CN';
      this.recognition.interimResults = false;
      this.recognition.maxAlternatives = 1;
      this.recognition.continuous = false;
      this.isSupported = true;
    }
    return this.isSupported;
  },

  // 开始监听
  start(onResult, onError) {
    if (!this.recognition) {
      if (onError) onError('浏览器不支持语音识别');
      return;
    }

    this.isListening = true;

    this.recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      this.isListening = false;
      if (onResult) onResult(text);
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      if (onError) onError(event.error);
    };

    this.recognition.onend = () => {
      this.isListening = false;
    };

    try {
      this.recognition.start();
    } catch (e) {
      this.isListening = false;
      if (onError) onError(e.message);
    }
  },

  // 停止监听
  stop() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  },

  // 是否正在监听
  get listening() {
    return this.isListening;
  }
};
