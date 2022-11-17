var charts = [ undefined, undefined, undefined ];

function make_chart(id, data, canvas,chart_type) {
    var ctx = document.getElementById(canvas);
    if (charts[id] != undefined) {
        charts[id].destroy();
    }

    charts[id] = new Chart(ctx, {
        type: chart_type,
        data: data,
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: "#F7F9F9",
                        font: {
                            size: 12
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: "#F7F9F9",
                    }
                },
                x: {
                    ticks: {
                        color: "#F7F9F9",
                    }
                },
            }
        }
    });
}

function update_chart(){
    var range = $('.datetimerange').data('daterangepicker');
    $.ajax({
        url: "/data/",
        data: jQuery.param({
            start: range.startDate.format('YYYY-MM-DD HH:MM'),
            end: range.endDate.format('YYYY-MM-DD HH:MM'),
        }),
    });
}

$(function() {   
   $('.datetimerange').daterangepicker({
        timePicker: true,
        startDate: moment().startOf('hour').subtract(24, 'hour'),
        endDate: moment().startOf('hour'),
        timePickerIncrement: 30,
        locale: {
            format: 'MM/DD/YYYY h:mm A'
        }
    });
    $('.datetimerange').on('apply.daterangepicker', function(ev,picker){
        update_chart();
    });
});
$(document).ready(update_chart)