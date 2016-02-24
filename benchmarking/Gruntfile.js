'use strict';
module.exports = function(grunt) {

  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    api_benchmark: {
      Nautilus: {
        options: {
          output: 'output_folder'
        },
        files: {
          'report.html': 'config.json',
          'export.json': 'config.json'
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-api-benchmark');
  grunt.registerTask('benchmark', ['api_benchmark']);
};