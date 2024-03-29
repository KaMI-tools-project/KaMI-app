$('.line').hover(function () {
    var $t = $(this);
    var $i = $('#' + $t.data('id'));
    let type = $t.attr('class').split(' ')[0];

    var ot = {
        x: $t.offset().left + $t.width() / 2,
        y: $t.offset().top + $t.height() / 2
    };
    var oi = {
        x: $i.offset().left + $i.width() / 2,
        y: $i.offset().top + $i.height() / 2
    };

    // x,y = top left corner
    // x1,y1 = bottom right corner
    var p = {
        x: ot.x < oi.x ? ot.x : oi.x,
        x1: ot.x > oi.x ? ot.x : oi.x,
        y: ot.y < oi.y ? ot.y : oi.y,
        y1: ot.y > oi.y ? ot.y : oi.y
    };
    // create canvas between those points
    var c = $('<canvas/>').attr({
        'width': p.x1 - p.x + 1,
        'height': p.y1 - p.y + 1
    }).css({
        'position': 'absolute',
        'left': p.x,
        'top': p.y,
        'z-index': 1,
        'opacity':0.65
    }).appendTo($('body'))[0].getContext('2d');

    // draw line
    if (type === "insertion"){
        color = "#4169E1"
    }if (type === "delSubts"){
        color= "#D2122E"
    }if(type==="exact-match"){
        color="#3CB371"
    }
    c.strokeStyle = color;
    c.lineCap = "round";
    //c.setLineDash([2, 4]);
    c.lineWidth = 5;
    c.beginPath();
    c.moveTo(ot.x - p.x, ot.y - p.y);
    c.lineTo(oi.x - p.x, oi.y - p.y);
    c.stroke();
    $($i).addClass('char')
    $($t).addClass('char')

}, function () {
    $('canvas').remove();
    $(".char").removeClass("char")
});