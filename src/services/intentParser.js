// 意图解析服务
class IntentParser {
    constructor() {
        this.navigationPatterns = [
            {
                pattern: /(?:导航|去|到|前往|从)(.+?)(?:到|至|去|前往)(.+)/,
                type: 'route_navigation',
                extract: (match) => ({
                    start: match[1].trim(),
                    end: match[2].trim()
                })
            },
            {
                pattern: /(?:导航|去|到|前往)(.+)/,
                type: 'destination_navigation',
                extract: (match) => ({
                    start: '当前位置',
                    end: match[1].trim()
                })
            },
            {
                pattern: /(?:从)(.+?)(?:出发|开始)/,
                type: 'start_navigation',
                extract: (match) => ({
                    start: match[1].trim(),
                    end: '未指定目的地'
                })
            }
        ];

        this.locationKeywords = {
            '北京': ['北京', '北京市', '京城', '帝都'],
            '上海': ['上海', '上海市', '申城', '魔都'],
            '广州': ['广州', '广州市', '羊城'],
            '深圳': ['深圳', '深圳市', '鹏城'],
            '杭州': ['杭州', '杭州市', '杭城'],
            '成都': ['成都', '成都市', '蓉城'],
            '武汉': ['武汉', '武汉市', '江城'],
            '西安': ['西安', '西安市', '长安'],
            '南京': ['南京', '南京市', '金陵'],
            '天津': ['天津', '天津市']
        };

        this.commonDestinations = {
            '机场': ['机场', '飞机场', '航空港'],
            '火车站': ['火车站', '高铁站', '动车站'],
            '汽车站': ['汽车站', '客运站', '长途车站'],
            '医院': ['医院', '人民医院', '中心医院'],
            '学校': ['学校', '大学', '学院', '中学'],
            '商场': ['商场', '购物中心', '百货'],
            '酒店': ['酒店', '宾馆', '旅馆'],
            '餐厅': ['餐厅', '饭店', '餐馆'],
            '加油站': ['加油站', '油站'],
            '家': ['家', '家里', '回家'],
            '公司': ['公司', '单位', '上班']
        };
    }

    parse(command) {
        console.log(`解析指令: ${command}`);

        // 清理指令文本
        const cleanedCommand = this.cleanCommand(command);

        // 尝试匹配导航模式
        const navigationResult = this.parseNavigation(cleanedCommand);
        if (navigationResult) {
            return navigationResult;
        }

        // 如果无法识别，返回默认结果
        return {
            type: 'unknown',
            confidence: 0.1,
            entities: {},
            originalCommand: command,
            parsedIntent: '无法识别的指令'
        };
    }

    cleanCommand(command) {
        return command
            .replace(/[请帮帮我]/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    parseNavigation(command) {
        for (const pattern of this.navigationPatterns) {
            const match = command.match(pattern.pattern);
            if (match) {
                const entities = pattern.extract(match);
                const normalizedEntities = this.normalizeLocations(entities);

                return {
                    type: pattern.type,
                    confidence: 0.9,
                    entities: normalizedEntities,
                    originalCommand: command,
                    parsedIntent: this.generateIntentDescription(pattern.type, normalizedEntities)
                };
            }
        }
        return null;
    }

    normalizeLocations(entities) {
        const normalized = { ...entities };

        // 标准化起点
        if (normalized.start && normalized.start !== '当前位置') {
            normalized.start = this.normalizeLocation(normalized.start);
        }

        // 标准化终点
        if (normalized.end && normalized.end !== '未指定目的地') {
            normalized.end = this.normalizeLocation(normalized.end);
        }

        return normalized;
    }

    normalizeLocation(location) {
        let normalized = location;

        // 标准化城市名称
        for (const [standard, variants] of Object.entries(this.locationKeywords)) {
            if (variants.some(variant => location.includes(variant))) {
                normalized = normalized.replace(new RegExp(variants.join('|'), 'g'), standard);
                break;
            }
        }

        // 标准化常见目的地
        for (const [standard, variants] of Object.entries(this.commonDestinations)) {
            if (variants.some(variant => location.includes(variant))) {
                // 保留完整地址，只标准化类型
                break;
            }
        }

        return normalized;
    }

    generateIntentDescription(type, entities) {
        switch (type) {
            case 'route_navigation':
                return `从 ${entities.start} 导航到 ${entities.end}`;
            case 'destination_navigation':
                return `导航到 ${entities.end}`;
            case 'start_navigation':
                return `从 ${entities.start} 出发`;
            default:
                return '导航指令';
        }
    }

    // 验证解析结果
    validateResult(result) {
        if (result.type === 'route_navigation') {
            if (!result.entities.start || !result.entities.end) {
                return {
                    valid: false,
                    error: '缺少起点或终点信息'
                };
            }
        } else if (result.type === 'destination_navigation') {
            if (!result.entities.end) {
                return {
                    valid: false,
                    error: '缺少目的地信息'
                };
            }
        }

        return { valid: true };
    }
}

export default IntentParser;