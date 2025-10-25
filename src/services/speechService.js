// 语音识别服务
import speech from '@google-cloud/speech';

class SpeechService {
    constructor() {
        // 初始化 Google Speech-to-Text 客户端
        // 注意：实际使用时需要配置 Google Cloud 凭据
        this.client = new speech.SpeechClient();

        // 配置语音识别参数
        this.request = {
            config: {
                encoding: 'LINEAR16',
                sampleRateHertz: 16000,
                languageCode: 'zh-CN',
                enableAutomaticPunctuation: true,
                model: 'default'
            },
            interimResults: false
        };
    }

    /**
     * 识别音频文件中的语音
     * @param {Buffer} audioBuffer 音频数据
     * @returns {Promise<string>} 识别出的文本
     */
    async recognizeSpeech(audioBuffer) {
        try {
            console.log('开始语音识别...');

            // 更新请求配置
            const request = {
                ...this.request,
                audio: {
                    content: audioBuffer.toString('base64')
                }
            };

            // 调用 Google Speech-to-Text API
            const [response] = await this.client.recognize(request);

            if (!response.results || response.results.length === 0) {
                throw new Error('没有识别到语音内容');
            }

            const transcription = response.results
                .map(result => result.alternatives[0].transcript)
                .join('\n');

            console.log(`语音识别结果: ${transcription}`);
            return transcription;

        } catch (error) {
            console.error('语音识别失败:', error);

            // 如果 Google Speech API 不可用，使用模拟识别
            if (error.code === 7 || error.message.includes('credentials')) {
                console.log('使用模拟语音识别');
                return this.mockSpeechRecognition();
            }

            throw new Error(`语音识别失败: ${error.message}`);
        }
    }

    /**
     * 模拟语音识别（用于开发和测试）
     */
    mockSpeechRecognition() {
        const mockCommands = [
            '导航从北京到上海',
            '去天安门广场',
            '从公司导航回家',
            '去最近的加油站',
            '从天安门到首都机场'
        ];

        const randomCommand = mockCommands[Math.floor(Math.random() * mockCommands.length)];
        console.log(`模拟语音识别结果: ${randomCommand}`);
        return randomCommand;
    }

    /**
     * 处理上传的音频文件
     * @param {Object} audioFile 音频文件对象
     * @returns {Promise<string>} 识别出的文本
     */
    async processAudioFile(audioFile) {
        try {
            // 将文件转换为 Buffer
            const audioBuffer = await this.fileToBuffer(audioFile);

            // 验证音频格式
            if (!this.validateAudioFormat(audioFile)) {
                throw new Error('不支持的音频格式，请使用 WAV 格式');
            }

            return await this.recognizeSpeech(audioBuffer);

        } catch (error) {
            console.error('处理音频文件失败:', error);
            throw error;
        }
    }

    /**
     * 将文件转换为 Buffer
     * @param {Object} file 文件对象
     * @returns {Promise<Buffer>}
     */
    async fileToBuffer(file) {
        return new Promise((resolve, reject) => {
            const chunks = [];

            file.on('data', (chunk) => {
                chunks.push(chunk);
            });

            file.on('end', () => {
                resolve(Buffer.concat(chunks));
            });

            file.on('error', (error) => {
                reject(error);
            });
        });
    }

    /**
     * 验证音频格式
     * @param {Object} file 文件对象
     * @returns {boolean}
     */
    validateAudioFormat(file) {
        const supportedFormats = ['audio/wav', 'audio/x-wav', 'audio/wave'];
        return supportedFormats.includes(file.mimetype);
    }

    /**
     * 获取支持的音频格式信息
     * @returns {Object}
     */
    getSupportedFormats() {
        return {
            formats: ['WAV'],
            sampleRate: 16000,
            channels: 1,
            encoding: 'LINEAR16'
        };
    }
}

export default SpeechService;