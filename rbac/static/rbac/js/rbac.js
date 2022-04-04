(function (jq) {
    jq('.multi-menu .title').click(function () {
        $(this).next().toggleClass('hide');
    //    next()该元素的下一个同级元素 toggleClass() 点一次加 点一次减这个类
    });
})(jQuery);