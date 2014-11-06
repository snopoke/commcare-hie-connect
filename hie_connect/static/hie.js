(function() {
  var hieApp;

  hieApp = angular.module('hieApp', []);

  hieApp.controller('HieController', function($scope, $http, $window) {
      $scope.records = [];
      $scope.currentPage = 0;
      $scope.numPerPage = 5;

      $scope.getRecords = function() {
          $http.get('/records.json' + '?page=' + $scope.currentPage).success(function(data) {
              return $scope.records = data;
          });
      };

      $scope.previousPage = function() {
          $scope.currentPage = Math.max(0, $scope.currentPage -1);
          $scope.getRecords();
      };

      $scope.nextPage = function() {
          $scope.currentPage += 1;
          $scope.getRecords();
      };

      $scope.getRecords();
  });

}).call(this);
