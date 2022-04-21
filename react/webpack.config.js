'use strict'

module.exports = (env) => {
  return {
    devtool: 'eval-source-map',
    mode: env.mode,
    entry: {
      IndexUsers: './src/index_users.js',
      Posts: './src/posts.js',
      CSRF: './src/csrf.js',
      MemberAdding: './src/adding_members.js',
      BigCalendar: './src/calendar.js'
    },
    resolve: {
      modules: [__dirname, 'node_modules'],
      extensions: ['.js', '.jsx', '.scss', '.css']
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
        },
        {
          test: /\.css/,
          use: ['style-loader', 'css-loader', 'sass-loader']
        }
      ]
    }
  }
}
