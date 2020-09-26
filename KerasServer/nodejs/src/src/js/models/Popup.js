define([
    "jquery"
], function($) {
    function PopupModel(popupId) {
        var self = this;

        function getPopup() {
            // ポップアップオブジェクトが存在しない場合, 生成
            return document.querySelector('#' + popupId);
          };

        function getPosition() {
            return { 
              my: { horizontal: 'left',
                    vertical: 'center'
                  },
              at: { horizontal: 'right',
                    vertical: 'center'
              },
              collision: 'fit' ,
              of: '' //'parent' 'window' document.querySelector('#xxx')
            }
          };

        /**
         * オープン時のイベントハンドラ
         */
        self.popupOpen = function (data, event) {
            oPopup = getPopup();
            if (oPopup) {
                if (event != undefined) {
                    oPopup.open(event.currentTarget, getPosition());
                } else {
                    oPopup.open();
                }
            }
        };

        /**
         * クローズ時のイベントハンドラ
         */
        self.popupClose = function (data, event) {
            oPopup = getPopup();
            if (oPopup) {
                oPopup.close();
            }
        };
    }

    return PopupModel;
});