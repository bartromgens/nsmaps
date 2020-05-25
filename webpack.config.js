var path = require("path");
var webpack = require('webpack');
var ManifestPlugin = require('webpack-manifest-plugin');
var WebpackCleanupPlugin = require('webpack-cleanup-plugin');
var ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = {
    context: __dirname,
    entry: {
        main: ["./website/main.js"],
        css: ["./website/css/nsmaps.css", "./node_modules/ol/ol.css"],
    },
    output: {
        library: ["NsMap"],
        libraryTarget: "var",
        path: path.join(__dirname, "website/build/"),
        filename: "[name].js"
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: "css-loader"
                })
            }
        ],
    },
    externals: {
//        jquery: "jQuery"
    },
    plugins: [
        new ManifestPlugin(),
        new ExtractTextPlugin("nsmaps.css"),
        new WebpackCleanupPlugin(),
    ],
};
