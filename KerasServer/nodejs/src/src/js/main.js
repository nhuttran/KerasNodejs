'use strict';

(function () {
  
  function _ojIsIE11() {
    var nAgt = navigator.userAgent;
    return nAgt.indexOf('MSIE') !== -1 || !!nAgt.match(/Trident.*rv:11./);
  };
  var _ojNeedsES5 = _ojIsIE11();

  requirejs.config(
    {
      baseUrl: 'js',
      paths:
      // injector:mainReleasePaths
      {
        'moment': 'libs/moment/moment',
        //'linq': 'libs/linq/linq',
        'knockout': 'libs/knockout/knockout-3.5.1.debug',
        'jquery': 'libs/jquery/jquery-3.5.1',
        'jqueryui-amd': 'libs/jquery/jqueryui-amd-1.12.1',
        'hammerjs': 'libs/hammer/hammer-2.0.8',
        'ojdnd': 'libs/dnd-polyfill/dnd-polyfill-1.0.2',
        'ojs': 'libs/oj/v9.0.0/debug' + (_ojNeedsES5 ? '_es5' : ''),
        'ojL10n': 'libs/oj/v9.0.0/ojL10n',
        'ojtranslations': 'libs/oj/v9.0.0/resources',
        'text': 'libs/require/text',
        'signals': 'libs/js-signals/signals',
        'customElements': 'libs/webcomponents/custom-elements.min',
        'proj4': 'libs/proj4js/dist/proj4-src',
        'css': 'libs/require-css/css.min',
        'touchr': 'libs/touchr/touchr',
        'corejs' : 'libs/corejs/shim',
        'chai': 'libs/chai/chai-4.2.0',
        'regenerator-runtime' : 'libs/regenerator-runtime/runtime'
      }
      // endinjector
    }
  );
}());

require([
  'ojs/ojbootstrap',
  'knockout',
  'appController',
  'ojs/ojlogger',
  'ojs/ojknockout',
  'ojs/ojmodule',
  'ojs/ojrouter',
  'ojs/ojnavigationlist',
  'ojs/ojbutton',
  'ojs/ojtoolbar'
], function (Bootstrap, ko, app, Logger) {
  Bootstrap.whenDocumentReady().then(
    function() {
      function init() {
        ko.applyBindings(app, document.getElementById('globalBody'));
      }

      window.addEventListener("focus", function(event) {
        app.authListener.refresh();
      });

      if (document.body.classList.contains('oj-hybrid')) {
        document.addEventListener("deviceready", init);
      } else {
        init();
      }

      $.ajaxSetup({
        cache: false,
        //crossDomain: true,
        xhrFields: {
          withCredentials: true
        }
      });
    }
  );
});
