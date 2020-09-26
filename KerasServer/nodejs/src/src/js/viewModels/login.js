define([
    '../utils/config',
    '../models/ApiClient',
    'ojs/ojbootstrap',
    'knockout',
    'ojs/ojknockout',
    'ojs/ojlabel',
    'ojs/ojinputtext',
    'ojs/ojbutton',
    'ojs/ojtoolbar'
], function(config, ApiClient, oj, ko) {
    function LoginViewModel() {
        var self = this;

        self.isDisabled = ko.observable(false);
        self.loginId = ko.observable("");
        self.password = ko.observable("");

        self.onLoginBtnClick = function (data, event) {
            // 入力チェックを行う
            var errMsg = inputCheck();
            if (errMsg != "") {
                alert(errMsg);
                return;
            }

            var client = new ApiClient();
            client.addData("loginId", self.loginId());
            client.addData("password", self.password());
            client.post('/auth/login', true)
            .done(function(resp, textStatus, jqXHR) {
                // エラーチェック
                if (client.isResponseError(resp)) {
                    return;
                }

                if (resp.loginStatus) {
                    sessionStorage.setItem("loginId", self.loginId());
                    document.location.href = config.app.HOME_URL;
                } else {
                    alert("ログインできません。ユーザIDとパスワードを再確認してください。");
                }
            });
        }

        /**
         * 初期表示
         */
        function initialize() {
            var loginId = sessionStorage.getItem("loginId");
            self.isDisabled(loginId != null);
        }

        initialize()

        /**
         * 入力チェック
         */
        function inputCheck() {
            var LINE_CHAR = "\n";
            var errMsg = "";
            if (self.loginId() == "") {
                errMsg += "ユーザIDが入力されていません。" + LINE_CHAR;
            }

            if (self.password() == "") {
                errMsg += "パスワードが入力されていません。" + LINE_CHAR;
            }

            return errMsg;
        }
    }

    return new LoginViewModel();
});