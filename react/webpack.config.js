'use strict'
module.exports = {
  devtool: 'eval-source-map',
  mode: 'development',
  entry: {
    IndexUsers: './src/index_users.js'
  },
  resolve: {
    modules: [__dirname, 'node_modules'],
    extensions: ['.js', '.jsx']
  },
  output: {
    path: '/src/upont/static/react/',
    filename: '[name].bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      }
    ]
  }
}
