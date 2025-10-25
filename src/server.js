// 主服务器文件
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

// 导入服务模块
import IntentParser from './services/intentParser.js';
import SpeechService from './services/speechService.js';
import NavigationService from './services/navigationService.js';
import AutomationClient from './mcp/automationClient.js';

// ES 模块的 __dirname 替代方案
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class NavigationServer {
    constructor() {
        this.app = express();
        this.server = createServer(this.app);
        this.io = new Server(this.server, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });

        // 初始化服务
        this.intentParser = new IntentParser();
        this.speechService = new SpeechService();
        this.navigationService = new NavigationService();
        this.automationClient = new AutomationClient();

        this.setupMiddleware();
        this.setupRoutes();
        this.setupSocketHandlers();
    }

    setupMiddleware() {
        // CORS 中间件
        this.app.use(cors());

        // 静态文件服务
        this.app.use(express.static(path.join(__dirname, '../public')));

        // JSON 解析中间件
        this.app.use(express.json({ limit: '10mb' }));

        // URL 编码解析中间件
        this.app.use(express.urlencoded({ extended: true }));
    }

    setupRoutes() {
        // 根路由
        this.app.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, '../public/index.html'));
        });

        // 健康检查
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                services: {
                    intentParser: 'active',
                    speechService: 'active',
                    navigationService: 'active',
                    automationClient: 'initializing'
                }
            });
        });

        // 语音命令处理
        this.app.post('/api/voice-command', async (req, res) => {
            try {
                // 注意：这里需要处理文件上传
                // 简化版本，实际使用时需要配置 multer 等文件上传中间件

                // 模拟语音识别结果
                const mockText = '导航从北京到上海';

                res.json({
                    success: true,
                    text: mockText,
                    confidence: 0.9
                });

            } catch (error) {
                console.error('语音命令处理失败:', error);
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // 获取系统状态
        this.app.get('/api/status', async (req, res) => {
            try {
                const automationStatus = await this.automationClient.initialize();

                res.json({
                    automation: {
                        connected: automationStatus,
                        tools: this.automationClient.getAvailableTools()
                    },
                    navigation: {
                        supportedMaps: this.navigationService.getSupportedMaps(),
                        defaultMap: this.navigationService.defaultMap
                    },
                    speech: {
                        supported: true,
                        formats: this.speechService.getSupportedFormats()
                    }
                });

            } catch (error) {
                console.error('获取系统状态失败:', error);
                res.status(500).json({
                    error: '获取系统状态失败'
                });
            }
        });
    }

    setupSocketHandlers() {
        this.io.on('connection', (socket) => {
            console.log('客户端连接:', socket.id);

            // 发送连接成功消息
            socket.emit('status_update', {
                message: '连接成功',
                icon: '✅'
            });

            // 处理导航命令
            socket.on('navigation_command', async (data) => {
                try {
                    await this.handleNavigationCommand(socket, data);
                } catch (error) {
                    console.error('处理导航命令失败:', error);
                    socket.emit('error', {
                        message: `处理命令失败: ${error.message}`
                    });
                }
            });

            // 处理断开连接
            socket.on('disconnect', () => {
                console.log('客户端断开连接:', socket.id);
            });
        });
    }

    async handleNavigationCommand(socket, data) {
        const { command, type } = data;

        // 更新状态
        socket.emit('status_update', {
            message: `处理${type === 'voice' ? '语音' : '文本'}指令...`,
            icon: '🔍'
        });

        // 解析意图
        const intent = this.intentParser.parse(command);
        console.log('解析后的意图:', intent);

        // 验证意图
        const validation = this.intentParser.validateResult(intent);
        if (!validation.valid) {
            socket.emit('error', {
                message: validation.error
            });
            return;
        }

        // 更新状态
        socket.emit('status_update', {
            message: `识别到: ${intent.parsedIntent}`,
            icon: '🗺️'
        });

        // 执行导航
        const navigationResult = await this.navigationService.executeNavigation(intent);

        if (navigationResult.success) {
            // 发送成功响应
            socket.emit('command_response', {
                originalCommand: command,
                parsedIntent: intent.parsedIntent,
                status: '成功',
                details: navigationResult.details
            });

            // 更新状态
            socket.emit('status_update', {
                message: '导航执行成功',
                icon: '✅'
            });

            // 执行自动化操作（可选）
            try {
                const automationResult = await this.automationClient.executeNavigationAutomation({
                    mapType: this.navigationService.defaultMap,
                    navigationUrl: navigationResult.details.url,
                    start: intent.entities.start,
                    end: intent.entities.end
                });

                if (automationResult.success) {
                    console.log('自动化操作执行成功');
                } else {
                    console.warn('自动化操作执行失败:', automationResult.error);
                }

            } catch (automationError) {
                console.warn('自动化操作执行异常:', automationError);
            }

        } else {
            // 发送错误响应
            socket.emit('error', {
                message: navigationResult.error
            });
        }
    }

    async start(port = 3000) {
        try {
            // 初始化自动化客户端
            await this.automationClient.initialize();

            // 启动服务器
            this.server.listen(port, () => {
                console.log(`🚀 AI 导航助手服务器已启动`);
                console.log(`📍 访问地址: http://localhost:${port}`);
                console.log(`🔧 健康检查: http://localhost:${port}/health`);
                console.log(`🤖 MCP 自动化: ${this.automationClient.connected ? '已连接' : '模拟模式'}`);
            });

        } catch (error) {
            console.error('服务器启动失败:', error);
            process.exit(1);
        }
    }
}

// 启动服务器
const server = new NavigationServer();
server.start(3000);

export default NavigationServer;