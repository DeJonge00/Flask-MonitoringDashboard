app.service('formService', function ($http, endpointService, $filter) {
    const SLICE = 10;

    let that = this;

    this.dateFields = [];
    this.multiFields = [];
    this.isLoading = true;

    this.clear = function () {
        that.multiFields = [];
        that.dateFields = [];
    };

    function addMultiSelect(name) {
        let obj = {
            'name': name,
            'values': [], // list of {id: , text: }
            'selected': [], // subset of 'items'
            'initialized': false
        };
        that.multiFields.push(obj);
        return obj;
    }

    this.initialize = function (obj) {
        obj.initialized = true;
        if (that.multiFields.every(o => o.initialized)) {
            that.reload();
        }
    };

    this.getMultiSelection = function (name) {

        return that.multiFields.find(o => o.name == name).selected.map(d=>d.id);
    };

    this.addDate = function (name) {
        let obj = {
            'name': name,
            'value': new Date(),
        };
        that.dateFields.push(obj);
        return obj;
    };

    this.getDate = function (name) {
        return parseDate(that.dateFields.find(o => o.name == name).value);
    };

    this.addVersions = function (endpoint_id) {
        let obj = addMultiSelect('versions');
        let url = 'api/versions';
        if (typeof endpoint_id !== "undefined") {
            url += '/' + endpoint_id;
        }
        $http.get(url).then(function (response) {
            obj.values = response.data.map(d => {
                    return {
                        id: d.version,
                        text: d.version + ' : ' + $filter('dateLayout')(d.date)
                    }
                }
            );
            obj.selected = obj.values.slice(-SLICE);
            that.initialize(obj);
        });
    };

    this.addEndpoints = function (rp_ip=null, rp_ports=[''], login_token=null, all_hosts=false) {
        let obj = addMultiSelect('endpoints');
        let data = {};

        rp_ports.forEach(function(port) {
            // Determine endpoint url
            let hits_url = 'api/endpoints_hits';
            if (all_hosts) {
                hits_url += '?host=all';
            }
            if (rp_ip != null) {
                hits_url = 'http://' + rp_ip + ':' + port + '/dashboard/' + hits_url;
            }
            // Skip redirect to login page
            if (login_token) {
                $http.defaults.headers.common['Authorization'] = login_token;
            }
            $http.get(hits_url).then(function (response) {
                // Add duplicate endpoints form multiple hosts
                response.data.forEach(function(d) {
                    if (!data[d.name]) { data[d.name] = 0; }
                    data[d.name] += d.hits;
                });

                // Add endpoint list to MultiSelect
                obj.values = [];
                for (let name in data) {
                    obj.values.push({
                        id: name,
                        text: name + ' : ' + data[name] + ' requests'
                    })
                }
                obj.selected = obj.values.slice(0, SLICE);
                that.initialize(obj);
            });
        });
    };

    this.addHosts = function(rp_ip=null, rp_ports=[''], login_token=null) {
        let obj = addMultiSelect('hosts');
        obj.values = [];
        rp_ports.forEach(function (port) {
            // Determine endpoint url
            let hits_url = 'api/host_hits';
            if (rp_ip != null) {
                hits_url = 'http://' + rp_ip + ':' + port + '/dashboard/' + hits_url;
            }
            // Skip redirect to login page
            if (login_token) {
                $http.defaults.headers.common['Authorization'] = login_token;
            }
            $http.get(hits_url).then(function (response) {
                // Add new hosts to the MultiSelect list
                response.data.forEach(d => {
                    obj.values.push({
                        id: d.name,
                        text: d.name + ' : ' + d.hits + ' total requests'
                    });
                });
                obj.selected = obj.values.slice(0, SLICE);
                that.initialize(obj);
            });
        })
    };

    this.addUsers = function () {
        let obj = addMultiSelect('users');
        $http.get('api/users/' + endpointService.info.id).then(function (response) {
            obj.values = response.data.map(d=>{
                return {
                    id: d.user,
                    text: d.user + ' : ' + d.hits + ' requests'
                }
            });
            obj.selected = obj.values.slice(0, SLICE);
            that.initialize(obj);
        });
    };

    this.addIP = function () {
        let obj = addMultiSelect('IP-addresses');
        $http.get('api/ip/' + endpointService.info.id).then(function (response) {
            obj.values = response.data.map(d=>{
                return {
                    id: d.ip,
                    text: d.ip + ' : ' + d.hits + ' requests'
                }
            });
            obj.selected = obj.values.slice(0, SLICE);
            that.initialize(obj);
        });
    };

    let parseDate = function (date) {
        return date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2)
            + "-" + ("0" + date.getDate()).slice(-2);
    };

    this.reload = function () {
    };
    this.setReload = function (f) {
        this.reload = function () {
            that.isLoading = true;
            f();
        };
    }
});