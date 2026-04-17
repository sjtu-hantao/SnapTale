# 使用官方 Node.js 18 镜像作为基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/base_mj/vmbook:frontend-latest

# 设置工作目录
WORKDIR /usr/src/app

# 安装 pnpm 包管理工具
RUN npm install -g pnpm

# 将 pnpm 配置文件和 lockfile 复制到工作目录
COPY pnpm-lock.yaml ./
COPY package.json ./

# 安装依赖项
RUN pnpm install

# 如果你只需要生产依赖，可以使用以下命令
# RUN pnpm install --prod

# 将当前目录中的所有文件复制到工作目录
COPY . .

# 如果你的应用程序需要构建步骤（例如 React 应用），你可以在这里添加
# RUN pnpm run build

# 暴露应用程序使用的端口（例如 3000）
EXPOSE 3000

# 运行应用程序
CMD [ "pnpm", "start" ]
