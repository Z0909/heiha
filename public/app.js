// 前端 JavaScript 应用逻辑
class NavigationApp {
    constructor() {
        this.socket = io();
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];

        this.initializeElements();
        this.setupEventListeners();
        this.setupSocketListeners();
    }

    initializeElements() {
        this.voiceBtn = document.getElementById('voiceBtn');
        this.voiceStatus = document.getElementById('voiceStatus');
        this.textInput = document.getElementById('textInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.recordingIndicator = document.getElementById('recordingIndicator');
        this.statusDisplay = document.getElementById('statusDisplay');
        this.resultDisplay = document.getElementById('resultDisplay');
        this.resultContent = document.getElementById('resultContent');
    }

    setupEventListeners() {
        // 语音按钮点击事件
        this.voiceBtn.addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });

        // 发送按钮点击事件
        this.sendBtn.addEventListener('click', () => {
            this.sendTextCommand();
        });

        // 回车键发送
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTextCommand();
            }
        });
    }

    setupSocketListeners() {
        // 连接状态
        this.socket.on('connect', () => {
            this.updateStatus('连接成功', '✅');
        });

        this.socket.on('disconnect', () => {
            this.updateStatus('连接断开', '❌');
        });

        // 处理服务器响应
        this.socket.on('command_response', (data) => {
            this.handleCommandResponse(data);
        });

        this.socket.on('status_update', (data) => {
            this.updateStatus(data.message, data.icon || 'ℹ️');
        });

        this.socket.on('error', (error) => {
            this.showError(error.message);
        });
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                await this.sendAudioCommand(audioBlob);

                // 停止所有音频轨道
                stream.getTracks().forEach(track => track.stop());
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.voiceBtn.classList.add('recording');
            this.voiceStatus.textContent = '停止录音';
            this.recordingIndicator.style.display = 'flex';
            this.updateStatus('正在录音...', '🎤');

        } catch (error) {
            console.error('录音失败:', error);
            this.showError('无法访问麦克风，请检查权限设置');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.voiceBtn.classList.remove('recording');
            this.voiceStatus.textContent = '开始录音';
            this.recordingIndicator.style.display = 'none';
            this.updateStatus('处理语音中...', '🔊');
        }
    }

    async sendAudioCommand(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob);

            const response = await fetch('/api/voice-command', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.socket.emit('navigation_command', {
                    command: result.text,
                    type: 'voice'
                });
            } else {
                this.showError('语音识别失败: ' + result.error);
            }

        } catch (error) {
            console.error('发送语音命令失败:', error);
            this.showError('语音命令发送失败');
        }
    }

    sendTextCommand() {
        const command = this.textInput.value.trim();
        if (!command) {
            this.showError('请输入导航指令');
            return;
        }

        this.socket.emit('navigation_command', {
            command: command,
            type: 'text'
        });

        this.textInput.value = '';
        this.updateStatus('处理指令中...', '🤔');
    }

    handleCommandResponse(data) {
        this.resultContent.innerHTML = `
            <div class="response-item">
                <strong>原始指令:</strong> ${data.originalCommand}
            </div>
            <div class="response-item">
                <strong>解析结果:</strong> ${data.parsedIntent}
            </div>
            <div class="response-item">
                <strong>执行状态:</strong> ${data.status}
            </div>
            ${data.details ? `<div class="response-item"><strong>详细信息:</strong> ${data.details}</div>` : ''}
        `;

        this.resultDisplay.style.display = 'block';
        this.updateStatus('指令执行完成', '✅');
    }

    updateStatus(message, icon = 'ℹ️') {
        this.statusDisplay.innerHTML = `
            <div class="status-item">
                <span class="status-icon">${icon}</span>
                <span class="status-text">${message}</span>
            </div>
        `;
    }

    showError(message) {
        this.updateStatus(message, '❌');

        // 显示错误信息在结果区域
        this.resultContent.textContent = message;
        this.resultDisplay.style.display = 'block';
        this.resultDisplay.style.background = '#ffebee';
        this.resultDisplay.style.borderColor = '#f44336';
    }
}

// 示例使用函数
function useExample(element) {
    const exampleText = element.textContent;
    document.getElementById('textInput').value = exampleText;
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new NavigationApp();
});