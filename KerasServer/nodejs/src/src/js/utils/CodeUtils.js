define([
], function() {
    var CodeUtils = {
        TRAIN_KIND: {
            VGG16: 0,
            VGG19: 1,
            VGG_FACE: 2
        },
        TRAIN_STATUS: {
            // 未依頼
            NONE: 0,
            // 依頼済
            SENDED: 1,
            // 学習準備
            READY: 2,
            // 学習中
            RUNNING: 3,
            // 学習済
            FINISHED: 4,
            // 適用中
            APPLYING: 5,
            // キャンセル
            CANCELED: 6,
            // 再依頼済
            RESENDED: 7,
            // エラー
            ERROR: 9
        }
    }

    return CodeUtils;
});