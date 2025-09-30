# Use Node.js 22 Alpine as base image
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port 4200
EXPOSE 4200

# Start the development server
CMD ["npm", "start", "--", "--host", "0.0.0.0"]
