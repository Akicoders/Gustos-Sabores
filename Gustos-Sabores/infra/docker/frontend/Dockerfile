FROM node:22-alpine

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./

EXPOSE 4321

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
