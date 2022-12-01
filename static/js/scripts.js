var charts = [ undefined, undefined, undefined ];

// Creates and updates main chart with provided data
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
    // if two datasets are present
    else {
        charts[id] = new Chart(ctx, {
        type: chart_type,
        data: {
            labels: data1["labels"],
                datasets: [{
                yAxisID: 'y',
                label: data1["datasets"][0]["label"],
                data: data1["datasets"][0]["data"],
                backgroundColor: '#702963',
                borderColor: '#702963',
                tension: data1["datasets"][0]["tension"],
                pointRadius: data1["datasets"][0]["pointRadius"],
                borderWidth: 3,
    
            },{
                yAxisID: 'y2',
                label: data2["datasets"][0]["label"],
                data: data2["datasets"][0]["data"],
                backgroundColor: '#FF7F00',
                borderColor: '#FF7F00',
                tension: data2["datasets"][0]["tension"],
                pointRadius: data2["datasets"][0]["pointRadius"],
                borderWidth: 3,

                }],

        },
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

// makes data chart from healthy limit & average user data
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
            
                data["datasets"][1],
            
            ],
        },
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
                r: {
                    min: 0,
                    max: 1.5,
                    beginAtZero: true,
                    ticks: {
                        color: "#F7F9F9",
                        backdropColor: "#424242", 
                        format: {
                            style: 'percent',
                        }
                    }
                }
            }
        }
    });

}




// creates / modifies charts based on date-time range 
function update_chart(id = 0, double = false){
    var range = $('.datetimerange').data('daterangepicker');    
    $.ajax({
        url: "/filter/",
        data: jQuery.param({
            begin: range.startDate.format("DD/MM/YYYY HH:MM"),
            end: range.endDate.format("DD/MM/YYYY HH:MM"),
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
        }
        
    });
}


// Determines which data is displayed
function change_mode(id = 0, mode){
    if(mode == localStorage.getItem('mode1')){
        localStorage.removeItem('mode1');
    }
    else if(mode == localStorage.getItem('mode2')){
        localStorage.removeItem('mode2');
    }
    else if(localStorage.getItem('mode1') == null){
        localStorage.setItem('mode1', mode);
    }
    else if(localStorage.getItem('mode2') == null){
        localStorage.setItem('mode2', mode);
    }
    else {
        localStorage.setItem('mode2', mode);
    }
    update_chart();


};
// Changes chart type (bar or line)
function change_type(id,chart_type){
    localStorage.setItem('c_type',chart_type);
    
    update_chart(id);
};


// Determines date-time range
$(function() {   
   $('.datetimerange').daterangepicker({
        timePicker: true,
        // startDate: moment().startOf('hour').subtract(24, 'hour'),
        // endDate: moment().startOf('hour'),
        startDate: '31/12/2021',
        endDate: '04/01/2022',
        timePickerIncrement: 30,
        locale: {
            //format: 'MM/DD/YYYY h:mm A'
            format: "DD/MM/YYYY HH:MM",
        },
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
