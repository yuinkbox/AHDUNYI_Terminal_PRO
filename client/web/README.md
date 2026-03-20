# Vue 3 + Arco Design 商业级前端应用

基于 Vue 3 + TypeScript + Arco Design 构建的企业级前端解决方案。

## 🚀 特性

- **现代化技术栈**: Vue 3 + TypeScript + Vite
- **企业级 UI**: 字节跳动 Arco Design 组件库
- **状态管理**: Pinia 状态管理
- **路由管理**: Vue Router 4
- **代码规范**: ESLint + Prettier + TypeScript 严格模式
- **开发体验**: 极速的 Vite 开发服务器
- **响应式设计**: 完整的移动端适配

## 📦 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的 JavaScript 超集
- **Arco Design Vue** - 字节跳动企业级 UI 组件库
- **Pinia** - Vue 官方推荐的状态管理库
- **Vue Router** - 官方路由管理器
- **Vite** - 下一代前端构建工具
- **VueUse** - Vue 组合式 API 实用工具集
- **Axios** - HTTP 客户端

## 🛠️ 开发环境

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0 或 pnpm >= 8.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
# 使用 npm
npm install

# 使用 pnpm
pnpm install

# 使用 yarn
yarn install
```

### 开发服务器

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint

# 代码格式化
npm run format
```

## 📁 项目结构

```
web_client/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 公共组件
│   ├── views/          # 页面组件
│   ├── router/         # 路由配置
│   ├── stores/         # Pinia 状态管理
│   ├── styles/         # 全局样式
│   ├── utils/          # 工具函数
│   ├── App.vue         # 根组件
│   └── main.ts         # 应用入口
├── public/             # 公共资源
├── index.html          # HTML 模板
├── package.json        # 依赖配置
├── vite.config.ts      # Vite 配置
├── tsconfig.json       # TypeScript 配置
└── README.md           # 项目说明
```

## 🎨 设计规范

### 颜色系统

使用 Arco Design 的颜色系统，主要颜色包括：

- **主色**: `#165dff` (蓝色)
- **成功色**: `#00b42a` (绿色)
- **警告色**: `#ff7d00` (橙色)
- **错误色**: `#f53f3f` (红色)

### 间距系统

使用统一的间距系统：

- `4px` (xs)
- `8px` (sm)
- `16px` (md)
- `24px` (lg)
- `32px` (xl)
- `48px` (xxl)

### 圆角系统

- `4px` (small)
- `6px` (medium)
- `8px` (large)

## 🔧 配置说明

### 环境变量

项目支持以下环境变量：

```env
VITE_APP_TITLE=商业级 Web 前端应用
VITE_APP_API_BASE_URL=/api
VITE_APP_MODE=development
```

### Vite 配置

查看 `vite.config.ts` 获取完整的构建配置，包括：

- 路径别名配置 (`@` → `src/`)
- 开发服务器配置
- 构建优化配置
- CSS 预处理器配置

### TypeScript 配置

项目使用严格的 TypeScript 配置，包括：

- 严格类型检查
- 路径别名支持
- Vue 3 类型支持
- 现代 JavaScript 特性

## 📱 响应式设计

项目使用 Arco Design 的响应式栅格系统，支持：

- **xs**: < 576px (手机)
- **sm**: ≥ 576px (平板)
- **md**: ≥ 768px (小桌面)
- **lg**: ≥ 992px (桌面)
- **xl**: ≥ 1200px (大桌面)
- **xxl**: ≥ 1600px (超大桌面)

## 🧪 测试

### 单元测试

```bash
# 运行单元测试
npm run test:unit

# 运行测试并生成覆盖率报告
npm run test:coverage
```

### E2E 测试

```bash
# 运行 E2E 测试
npm run test:e2e
```

## 📄 代码规范

### 提交规范

使用 Conventional Commits 规范：

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

### 代码检查

项目配置了 ESLint 和 Prettier，确保代码质量：

```bash
# 检查代码规范
npm run lint

# 自动修复代码规范问题
npm run lint -- --fix

# 格式化代码
npm run format
```

## 🚢 部署

### 构建生产版本

```bash
npm run build
```

构建产物将生成在 `dist/` 目录下。

### 部署到静态服务器

可以将 `dist/` 目录部署到任何静态服务器，如：

- Nginx
- Apache
- Vercel
- Netlify
- GitHub Pages

### Docker 部署

```dockerfile
# 使用多阶段构建
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📚 学习资源

- [Vue 3 官方文档](https://vuejs.org/)
- [Arco Design Vue 文档](https://arco.design/vue/docs/start)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)
- [Vite 官方文档](https://vitejs.dev/)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源。

## 🙏 致谢

感谢以下开源项目的贡献：

- [Vue.js](https://vuejs.org/)
- [Arco Design](https://arco.design/)
- [Vite](https://vitejs.dev/)
- [Pinia](https://pinia.vuejs.org/)
- [Vue Router](https://router.vuejs.org/)

---

**Happy Coding!** 🎉