FROM node:17.6.0
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
CMD npm run build && npx serve -s bundles