FROM node:24-slim

RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser/app

COPY server.js .

EXPOSE 3000
CMD ["node", "server.js"]
