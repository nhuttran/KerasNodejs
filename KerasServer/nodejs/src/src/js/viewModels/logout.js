define([
    '../utils/config',
    '../models/ApiClient'
],function(config, ApiClient) {
    function LogoutViewModel() {
        /**
         * 初期表示
         */
        function initialize() {
            var client = new ApiClient();
            client.get('/auth/logout', {}, false)
            .done(function(resp, textStatus, jqXHR) {
                sessionStorage.clear();
                // ログイン画面へ遷移する
                document.location.href = config.app.LOGIN_URL;
            });
        }

        initialize()
    }

    return new LogoutViewModel();
});