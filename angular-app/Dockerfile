# ============================================
# QueueLess Clinic - Angular Frontend Dockerfile
# ============================================

# Stage 1: Build Angular app
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with explicit retry loop for transient network errors
RUN npm config set fetch-retries 8 \
	&& npm config set fetch-retry-factor 10 \
	&& npm config set fetch-retry-mintimeout 20000 \
	&& npm config set fetch-retry-maxtimeout 180000 \
	&& npm config set fetch-timeout 300000 \
	&& npm config set registry https://registry.npmjs.org/ \
	&& ok=0 \
	&& for i in 1 2 3 4 5; do \
		if npm ci --no-audit --no-fund; then ok=1; break; fi; \
		echo "npm ci failed (attempt $i), retrying..."; \
		npm cache clean --force; \
		sleep 8; \
	done \
	&& test "$ok" = "1"

# Copy source code
COPY . .

# Build Angular app for production
RUN npm run build -- --configuration production

# Stage 2: Development (with hot reload)
FROM node:20-alpine AS development

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with explicit retry loop for transient network errors
RUN npm config set fetch-retries 8 \
	&& npm config set fetch-retry-factor 10 \
	&& npm config set fetch-retry-mintimeout 20000 \
	&& npm config set fetch-retry-maxtimeout 180000 \
	&& npm config set fetch-timeout 300000 \
	&& npm config set registry https://registry.npmjs.org/ \
	&& ok=0 \
	&& for i in 1 2 3 4 5; do \
		if npm ci --no-audit --no-fund; then ok=1; break; fi; \
		echo "npm ci failed (attempt $i), retrying..."; \
		npm cache clean --force; \
		sleep 8; \
	done \
	&& test "$ok" = "1"

# Copy source code
COPY . .

# Expose port
EXPOSE 4200

# Start development server with hot reload
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "2000"]

# Stage 3: Production (serve with nginx)
FROM nginx:alpine AS production

# Copy built app from builder stage (Angular outputPath)
COPY --from=builder /app/dist/queueless-frontend /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
