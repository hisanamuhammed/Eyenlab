 //COUPON
$(document).on('click', '#apply_coupon',function () {

    var coupon_code = $("[name='coupon_code']").val();
    var order_number = $('.order_number').attr('order_number');
    console.log(order_number, coupon_code);

    //ajax
    $.ajax({
        url: "/orders/apply-coupon/",
        data: {
            'coupon_code':coupon_code,
            'order_number':order_number
        },
        dataType: "json",
        success: function (res) {
            console.log(res);
            if (res.msg=='Coupon is Applied') {
                swal.fire("Congratulations ! ", res.msg, "success")
                $('#payment_render').html(res.data);
            } else{
                swal.fire({
                    icon:'error',
                    title:'Sorry',
                    text: res.msg,
                })
                console.log(res.msg);
            }
        }
    });
    //End Ajax
    
});
//End coupon