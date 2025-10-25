// 简单的 MCP 自动化服务器示例
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// 创建 MCP 服务器
const server = new Server(
  {
    name: 'navigation-automation-server',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// 注册工具
server.setRequestHandler({
  tools: async () => {
    return {
      tools: [
        {
          name: 'open_browser',
          description: '打开浏览器',
          inputSchema: {
            type: 'object',
            properties: {},
            required: []
          }
        },
        {
          name: 'navigate_to_url',
          description: '导航到指定URL',
          inputSchema: {
            type: 'object',
            properties: {
              url: {
                type: 'string',
                description: '要导航的URL'
              }
            },
            required: ['url']
          }
        },
        {
          name: 'type_text',
          description: '在输入框中输入文本',
          inputSchema: {
            type: 'object',
            properties: {
              text: {
                type: 'string',
                description: '要输入的文本'
              },
              selector: {
                type: 'string',
                description: 'CSS选择器'
              }
            },
            required: ['text', 'selector']
          }
        },
        {
          name: 'click_element',
          description: '点击页面元素',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS选择器'
              }
            },
            required: ['selector']
          }
        },
        {
          name: 'wait_for_element',
          description: '等待元素出现',
          inputSchema: {
            type: 'object',
            properties: {
              selector: {
                type: 'string',
                description: 'CSS选择器'
              },
              timeout: {
                type: 'number',
                description: '超时时间（毫秒）'
              }
            },
            required: ['selector']
          }
        },
        {
          name: 'take_screenshot',
          description: '截取屏幕截图',
          inputSchema: {
            type: 'object',
            properties: {},
            required: []
          }
        }
      ]
    };
  }
});

// 处理工具调用
server.setRequestHandler({
  callTool: async (request) => {
    const { name, arguments } = request.params;

    console.log(`调用工具: ${name}`, arguments);

    switch (name) {
      case 'open_browser':
        return {
          content: [
            {
              type: 'text',
              text: '浏览器已打开'
            }
          ]
        };

      case 'navigate_to_url':
        return {
          content: [
            {
              type: 'text',
              text: `已导航到: ${arguments.url}`
            }
          ]
        };

      case 'type_text':
        return {
          content: [
            {
              type: 'text',
              text: `已输入文本: "${arguments.text}" 到元素: ${arguments.selector}`
            }
          ]
        };

      case 'click_element':
        return {
          content: [
            {
              type: 'text',
              text: `已点击元素: ${arguments.selector}`
            }
          ]
        };

      case 'wait_for_element':
        return {
          content: [
            {
              type: 'text',
              text: `已等待元素: ${arguments.selector}`
            }
          ]
        };

      case 'take_screenshot':
        return {
          content: [
            {
              type: 'text',
              text: '截图已保存'
            }
          ]
        };

      default:
        throw new Error(`未知的工具: ${name}`);
    }
  }
});

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP 自动化服务器已启动');
}

main().catch((error) => {
  console.error('服务器启动失败:', error);
  process.exit(1);
});