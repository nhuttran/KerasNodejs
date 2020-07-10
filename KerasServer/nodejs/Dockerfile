FROM node:14.5.0

LABEL maintainer="Tran Quoc Nhut <qnhut.tran@gmail.com>"
LABEL title="NodeJs"

# https://www.npmjs.com/package/npm/v/3.10.8
RUN useradd --user-group --create-home --shell /bin/false app &&\
  npm install npm@3.10.8 -g

# node.js の環境変数を定義する
ENV WORKING_DIR=/opt/nodejskeras
ENV WEB_CLIENT_PATH=$WORKING_DIR/client
RUN mkdir -p $WORKING_DIR
RUN mkdir -p $WEB_CLIENT_PATH

COPY ./package.json $WEB_CLIENT_PATH
RUN chown -R app:app $WORKING_DIR/*

USER app

# ディレクトリを移動する
WORKDIR ${WEB_CLIENT_PATH}
RUN npm install

CMD ["node", "index.js"]