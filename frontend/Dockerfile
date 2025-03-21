# Base image
FROM node:14-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package.json .
COPY package-lock.json .

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

# Expose port 3000
EXPOSE 3000

# Start the app
CMD ["npm", "run", "build"]
