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
      PochtronShop: './src/pochtron_shop.js',
      PochtronManageAccounts: './src/pochtron_manage_accounts.js'
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
}
