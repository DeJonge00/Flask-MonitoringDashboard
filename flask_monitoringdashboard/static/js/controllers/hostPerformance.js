//TODO Alert user that the data on this webpage is retrieved from multiple sources, unlike the other pages (like API performance)

function HostPerformanceController($scope, $http, menuService, formService, infoService,
                                   plotlyService, endpointService) {
    endpointService.reset();
    menuService.reset('host_performance');
    $scope.title = 'Host Performance';

    // Set the information box
    infoService.axesText = 'The X-axis presents the execution time in ms. The Y-axis presents every connected host of' +
        ' the Flask application.';
    infoService.contentText = 'In this graph, it is easy to compare the execution times of different endpoints. ' +
        'This information can be used to discover which endpoints need to be improved in terms ' +
        'of response times.';

    // Set the form handler
    formService.clear();

    // Retrieve the locations where the other hosts machines can be found
    $http.get('api/deploy_container_config').then(function (response) {
        const reverse_proxy_ip = response.data.reverse_proxy_ip;
        const reverse_proxy_ports = response.data.reverse_proxy_ports;

        // Showing all endpoints from all hosts on the webpage
        const login_token = 'Bearer admin:admin'; //TODO retrieve un+pw from config
        formService.addHosts(reverse_proxy_ip, reverse_proxy_ports, login_token);
        formService.addEndpoints(reverse_proxy_ip, reverse_proxy_ports, login_token, true);

        formService.setReload(function () {
            let host_performance_data = [];
            reverse_proxy_ports.forEach(function (port) {
                let url = 'api/host_performance';
                if (reverse_proxy_ip) {
                    url = 'http://' + reverse_proxy_ip + ':' + port + '/dashboard/' + url;
                }

                // Retrieve host performance data from every host
                // Skip redirect to login page
                if (login_token) {
                    $http.defaults.headers.common['Authorization'] = login_token;
                }
                $http.post(url, {
                    data: {
                        ids: formService.getMultiSelection('hosts'),
                        endpoints: formService.getMultiSelection('endpoints')
                    }
                }).then(function (response) {
                    // Add data from all hosts (so far) together
                    response.data.map(obj => {
                        host_performance_data.push({
                            x: obj.values,
                            type: 'box',
                            name: obj.name + ' (id=' + obj.id + ')',
                            id: obj.id
                        });
                    });

                    // Build and show chart on the webpage
                    plotlyService.chart(host_performance_data, {
                        xaxis: {
                            title: 'Execution time (ms)',
                        },
                        yaxis: {
                            type: 'category'
                        }
                    });
                }).catch(console.error);
            });
        });
    });
}