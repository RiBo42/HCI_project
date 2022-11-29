var charts = [ undefined, undefined, undefined ];
var steps = document.getElementById("Steps");
var modes = [undefined, undefined];
// localStorage.setItem('d1', null);
// localStorage.setItem('d2', null);

function make_chart(id, data1, data2, canvas, chart_type) {
    var ctx = document.getElementById(canvas);
    if (charts[id] != undefined) {
        charts[id].destroy();
    }
    if(data2 == undefined){
        charts[id] = new Chart(ctx, {
        type: chart_type,
        data: data1,
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: "#F7F9F9",
                        font: {
                            size: 12
                        }
                    }
                },
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
    else if(data1 == undefined){
        charts[id] = new Chart(ctx, {
        type: chart_type,
        data: data2,
        options: {
            plugins: {
                legend: {
                    labels: {
                        color: "#F7F9F9",
                        font: {
                            size: 12
                        }
                    }
                },
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
    else {
        charts[id] = new Chart(ctx, {
        type: chart_type,
        data: {
            labels: data1["labels"],
                datasets: [{
                yAxisID: 'y',
                label: data1["datasets"][0]["label"],
                data: data1["datasets"][0]["data"],
                borderWidth: 1,
                backgroundColor: 'blue',
                borderColor: 'blue',
                tension: data1["datasets"][0]["tension"]
    
            },{
                yAxisID: 'y2',
                label: data2["datasets"][0]["label"],
                data: data2["datasets"][0]["data"],
                borderWidth: 1,
                backgroundColor: 'green',
                borderColor: 'green',
                tension: data2["datasets"][0]["tension"],

                }],

        },
        options: {
            scales: {
                y: {
                    position: 'left',
                    type: 'linear',
                    beginAtZero: true,
                    ticks: {
                        color: "#F7F9F9",
                    },
                },
                y2: {
                    position: 'right',
                    type: 'linear',
                    ticks: {

                        color: "#F7F9F9",
                    },

                },
                x: {
                    ticks: {
                        color: "#F7F9F9",
                    },
                },
            }
        }
    }); 

    }


}

// function make_double_chart(id, data1, data2, canvas, chart_type) {
//     var ctx = document.getElementById(canvas);
//     if (charts[id] != undefined) {
//         charts[id].destroy();
//     }

    
// }

function make_radar_chart(id, data, canvas){
    var ctx = document.getElementById(canvas);
    if (charts[id] != undefined) {
        charts[id].destroy();
    }
    charts[id] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data["labels"],
            datasets: [
                data["datasets"][0],

                // label: data["datasets"][0]["label"],
                // data: data["datasets"][0]["data"],
                // borderWidth: 2,
                // backgroundColor: data["datasets"][0]["backgroundColor"]
                // borderColor: data["datasets"][0]["borderColor"],
            
                data["datasets"][1],
            
            ],


        },
        options: {
            scales: {
                r: {
                    min: 0,
                    max: 1.5,
                    beginAtZero: true,
                    ticks: {
                        format: {
                            style: 'percent',
                        }
                    }
                }
            }
        }
    });

}





function update_chart(id = 0, double = false){
    var range = $('.datetimerange').data('daterangepicker');    
    //console.log(range.startDate.format('YYYY-MM-DD HH:MM'));
    $.ajax({
        url: "/filter/",
        data: jQuery.param({
            begin: range.startDate.format('YYYY-MM-DD HH:MM'),
            end: range.endDate.format('YYYY-MM-DD HH:MM'),
        }),
        success: function(response) {
            if(localStorage.getItem('c_type') == null){
                make_chart(id,response["hb"],"hb","line");
            }
            else{
                make_chart(id,response[localStorage.getItem('mode1')],
                    response[localStorage.getItem('mode2')],"hb",localStorage.getItem('c_type'));

            }
            make_radar_chart(1, response["radar"], "radar");
            //make_chart(1,response["radar"],unde,"radar","radar");
        }
        
    });
}

function change_mode(id = 0, mode){
    if(mode == localStorage.getItem('mode1')){
        console.log("model1 is not null")
        localStorage.removeItem('mode1');
    }
    else if(mode == localStorage.getItem('mode2')){
        localStorage.removeItem('mode2');
    }
    else if(localStorage.getItem('mode1') == null){
        console.log("model1 is null")
        localStorage.setItem('mode1', mode);
    }
    else if(localStorage.getItem('mode2') == null){
        localStorage.setItem('mode2', mode);
        console.log("model2 is null")
    }
    else {
        console.log("model12 is not null")
        localStorage.removeItem('mode2');
    }
    update_chart();


};

function change_type(id,chart_type){
    //localStorage.removeItem('c_type');
    localStorage.setItem('c_type',chart_type);
    
    update_chart(id);
};



$(function() {   
   $('.datetimerange').daterangepicker({
        timePicker: true,
        startDate: moment().startOf('hour').subtract(24, 'hour'),
        endDate: moment().startOf('hour'),
        timePickerIncrement: 30,
        locale: {
            //format: 'MM/DD/YYYY h:mm A'
            format: "YYYY-MM-DD HH:MM"
        }
    });
    $('.datetimerange').on('apply.daterangepicker', function(ev,picker){
        update_chart(0);
    });
});
//$(document).ready(update_chart())
$(document).ready(function(){
    update_chart(0);
    console.log(localStorage.getItem('mode1'))
    console.log(localStorage.getItem('mode2'))

});
