// 导航服务 - 处理地图导航逻辑
import open from 'open';

class NavigationService {
    constructor() {
        this.supportedMaps = {
            'baidu': {
                name: '百度地图',
                baseUrl: 'https://map.baidu.com',
                navigationUrl: 'https://map.baidu.com/dir/{start}/@{end}/'
            },
            'gaode': {
                name: '高德地图',
                baseUrl: 'https://ditu.amap.com',
                navigationUrl: 'https://uri.amap.com/navigation?from={start}&to={end}'
            }
        };

        this.defaultMap = 'baidu';
    }

    /**
     * 执行导航操作
     * @param {Object} intent 解析后的意图
     * @param {string} mapType 地图类型 ('baidu' 或 'gaode')
     * @returns {Promise<Object>} 执行结果
     */
    async executeNavigation(intent, mapType = this.defaultMap) {
        try {
            console.log('执行导航:', intent);

            // 验证意图
            const validation = this.validateNavigationIntent(intent);
            if (!validation.valid) {
                throw new Error(validation.error);
            }

            // 验证地图类型
            if (!this.supportedMaps[mapType]) {
                throw new Error(`不支持的地图类型: ${mapType}`);
            }

            // 生成导航 URL
            const navigationUrl = this.generateNavigationUrl(intent.entities, mapType);

            // 打开地图应用
            await this.openMap(navigationUrl, mapType);

            return {
                success: true,
                message: `成功打开${this.supportedMaps[mapType].name}导航`,
                details: {
                    start: intent.entities.start,
                    end: intent.entities.end,
                    map: this.supportedMaps[mapType].name,
                    url: navigationUrl
                }
            };

        } catch (error) {
            console.error('导航执行失败:', error);
            return {
                success: false,
                error: error.message,
                details: {
                    intent: intent,
                    mapType: mapType
                }
            };
        }
    }

    /**
     * 验证导航意图
     * @param {Object} intent 意图对象
     * @returns {Object} 验证结果
     */
    validateNavigationIntent(intent) {
        if (!intent || !intent.entities) {
            return {
                valid: false,
                error: '无效的导航意图'
            };
        }

        const { start, end } = intent.entities;

        if (intent.type === 'route_navigation') {
            if (!start || start === '当前位置') {
                return {
                    valid: false,
                    error: '路线导航需要指定起点'
                };
            }
            if (!end || end === '未指定目的地') {
                return {
                    valid: false,
                    error: '路线导航需要指定终点'
                };
            }
        } else if (intent.type === 'destination_navigation') {
            if (!end || end === '未指定目的地') {
                return {
                    valid: false,
                    error: '目的地导航需要指定终点'
                };
            }
        }

        return { valid: true };
    }

    /**
     * 生成导航 URL
     * @param {Object} entities 位置实体
     * @param {string} mapType 地图类型
     * @returns {string} 导航 URL
     */
    generateNavigationUrl(entities, mapType) {
        const mapConfig = this.supportedMaps[mapType];
        let url = mapConfig.navigationUrl;

        const { start, end } = entities;

        // 处理起点和终点
        const encodedStart = this.encodeLocation(start, mapType);
        const encodedEnd = this.encodeLocation(end, mapType);

        // 替换 URL 中的占位符
        url = url.replace('{start}', encodedStart)
                 .replace('{end}', encodedEnd);

        return url;
    }

    /**
     * 编码位置信息
     * @param {string} location 位置字符串
     * @param {string} mapType 地图类型
     * @returns {string} 编码后的位置
     */
    encodeLocation(location, mapType) {
        if (location === '当前位置') {
            return mapType === 'baidu' ? 'mypos' : 'here';
        }

        // 对位置进行 URL 编码
        return encodeURIComponent(location);
    }

    /**
     * 打开地图应用
     * @param {string} url 导航 URL
     * @param {string} mapType 地图类型
     * @returns {Promise<void>}
     */
    async openMap(url, mapType) {
        try {
            console.log(`打开${this.supportedMaps[mapType].name}: ${url}`);

            // 使用 open 库打开浏览器
            await open(url);

            console.log(`成功打开${this.supportedMaps[mapType].name}`);

        } catch (error) {
            console.error(`打开${this.supportedMaps[mapType].name}失败:`, error);
            throw new Error(`无法打开${this.supportedMaps[mapType].name}: ${error.message}`);
        }
    }

    /**
     * 获取支持的地图列表
     * @returns {Array} 地图列表
     */
    getSupportedMaps() {
        return Object.keys(this.supportedMaps).map(key => ({
            id: key,
            name: this.supportedMaps[key].name,
            baseUrl: this.supportedMaps[key].baseUrl
        }));
    }

    /**
     * 设置默认地图
     * @param {string} mapType 地图类型
     */
    setDefaultMap(mapType) {
        if (this.supportedMaps[mapType]) {
            this.defaultMap = mapType;
            console.log(`默认地图已设置为: ${this.supportedMaps[mapType].name}`);
        } else {
            throw new Error(`不支持的地图类型: ${mapType}`);
        }
    }
}

export default NavigationService;