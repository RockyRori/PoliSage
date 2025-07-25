# PoliSage

## 项目目录

```struct
PoliSage/
├── .gitignore                  # 忽略敏感文件、编译产物等
├── README.md                   # 项目简介、快速开始、架构概览
│
├── backend/                    # 后端服务（Python/Flask、FastAPI 等）
│   ├── src/
│   │   ├── api/                # 路由层：REST/GraphQL 接口
│   │   ├── core/               # 核心逻辑：检索、生成、向量处理
│   │   ├── models/             # ORM/数据模型定义
│   │   ├── services/           # 与 Qdrant、存储、授权等外部系统交互
│   │   └── utils/              # 日志、安全、配置加载等通用工具
│   │
│   ├── tests/                  # 单元测试、集成测试
│   │   ├── api/                
│   │   └── core/
│   │
│   ├── requirements.txt        # Python 依赖
│   ├── Dockerfile              # 后端容器化配置
│   └── config/
│       ├── dev.yml             # 开发环境配置
│       └── prod.yml            # 生产环境配置
│
├── frontend/                   # 前端应用（React/Vue/Next.js 等）
│   ├── public/                 # 静态资源（favicon、index.html）
│   ├── src/
│   │   ├── assets/             # 图片、样式、图标等
│   │   ├── components/         # 复用组件
│   │   ├── pages/              # 页面路由/视图
│   │   ├── store/              # 状态管理（Redux/Vuex/MobX）
│   │   ├── services/           # API 调用封装
│   │   └── utils/              # 通用工具函数
│   │
│   ├── tests/                  # 前端测试（Jest、Cypress 等）
│   ├── package.json            # 前端依赖与启动脚本
│   └── vite.config.js          # 构建工具配置（或 webpack.config.js）
│
├── database/                   # 数据层：模式、迁移、示例数据
│   ├── migrations/             # Alembic/Flyway/Knex 迁移脚本
│   ├── schema/                 # ER 图、表定义文档（.sql/.ddl）
│   ├── seeds/                  # 初始化种子数据
│   └── qdrant/                 # Qdrant collection 定义 & 索引脚本
│
├── deploy/                     # 部署与运维
│   ├── k8s/                    # Kubernetes manifests (Deployment, Service)
│   ├── helm/                   # Helm charts（可选）
│   ├── docker-compose.yml      # 本地/开发环境一键启动
│   ├── scripts/                # CI/CD 脚本（build.sh、deploy.sh）
│   └── terraform/              # 基础设施即代码（可选）
│
└── docs/                       # 文档
    ├── architecture.md         # 系统架构图与说明
    ├── api.md                  # REST/GraphQL 接口规范
    ├── data-flow.md            # 数据流程与向量检索说明
    ├── dev-guide.md            # 本地开发与调试指南
    └── ops-guide.md            # 上线、监控、告警手册

```