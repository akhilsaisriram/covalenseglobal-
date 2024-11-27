FROM node:22-alpine

WORKDIR /app

COPY package*.json .

RUN npm install

COPY . .

ENV PORT=5173

# CMD ["npm", "start"]
CMD ["sh", "-c", "npm run dev"]
