# Dockerfile for frontend
FROM node:16

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the React app for production (if not in development)
RUN npm run build

# Expose the port that React app runs on
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
