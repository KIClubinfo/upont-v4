'use strict'

// entryMap is an object containing all entrypoints (files under ./src/pages)
const fs = require('fs')
const entryMap = {}
fs.readdirSync('./src/pages/')
  .filter(file => {
    return file.match(/.*\.(j|t)sx?$/)
  })
  .forEach(file => {
    entryMap[file.replace(/\.(j|t)sx?$/, '')] = './src/pages/' + file
  })

module.exports = (env) => {
  return {
    devtool: 'eval-source-map',
    mode: env.mode,
    entry: entryMap,
    resolve: {
      modules: [__dirname, 'node_modules'],
      extensions: ['.js', '.jsx', '.ts', '.tsx']
    },
    output: {
      path: '/src/upont/static/react/',
      filename: '[name].bundle.js'
    },
    module: {
      rules: [
        { test: /\.tsx?$/, loader: 'ts-loader' },
        { test: /\.jsx?$/, loader: 'babel-loader' }
      ]
    }
  }
}
