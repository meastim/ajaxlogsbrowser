(function($) {
	function SyslogRemoteModel() {
		// private
		var PAGESIZE = 100;
		var data = {
			length : 0
		};

		var tabIndex = 0;

		var searchDateTime = "";
		var allDays = "0";

		var host = "";
		var facility = "";
		var levelThreshold = 0;
		var syslogTagPrefix = "";

		var h_request = null;
		var req = null;

		// events
		var onDataLoading = new Slick.Event();
		var onDataLoaded = new Slick.Event();

		function init() {
		}

		function isDataLoaded(from, to) {
			for ( var i = from; i <= to; i++) {
				if (data[i] == undefined || data[i] == null) {
					return false;
				}
			}

			return true;
		}

		function clear() {
			var getItemMetadata = data.getItemMetadata;
			for ( var key in data) {
				delete data[key];
			}
			data.getItemMetadata = getItemMetadata;
			data.length = 0;
		}

		function ensureData(from, to, autoScroll) {
			if (req) {
				req.abort();
				for ( var i = req.fromPage; i <= req.toPage; i++)
					delete data[i * PAGESIZE];
			}

			if (from < 0) {
				from = 0;
			}

			var fromPage = Math.floor(from / PAGESIZE);
			var toPage = Math.floor(to / PAGESIZE);
			var lastPage = Math.floor(data.length / PAGESIZE);

			while (data[fromPage * PAGESIZE] !== undefined && fromPage < toPage)
				fromPage++;

			if (toPage != lastPage) {
				while (data[toPage * PAGESIZE] !== undefined
						&& fromPage < toPage)
					toPage--;
			}

			if ((fromPage > toPage)
					|| ((fromPage == toPage) && (toPage != lastPage) && data[fromPage
							* PAGESIZE] !== undefined)) {
				return;
			}

			var url = "ajax?date="
					+ encodeURIComponent(searchDateTime) + "&host="
					+ encodeURIComponent(host) + "&facility="
					+ encodeURIComponent(facility) + "&thres=" + levelThreshold
					+ "&tagprefix=" + encodeURIComponent(syslogTagPrefix)
					+ "&fromPage=" + fromPage + "&pageCount="
					+ (toPage - fromPage + 1) + "&pageSize=" + PAGESIZE
					+ "&alldays=" + allDays + "&tabindex=" + tabIndex;

			if (h_request != null) {
				clearTimeout(h_request);
			}

			h_request = setTimeout(function() {
				for ( var i = fromPage; i <= toPage; i++) {
					delete data[i * PAGESIZE];
				}

				onDataLoading.notify({
					fromPage : fromPage,
					toPage : toPage
				});

				req = $.ajax({
					url : url,
					dataType : 'json',
					success : onSuccess,
					error : function() {
						onError(fromPage, toPage);
					}
				});
				req.fromPage = fromPage;
				req.toPage = toPage;
				req.autoScroll = autoScroll;
			}, 50);
		}

		function onError(fromPage, toPage) {
			console.log("error loading pages " + fromPage + " to " + toPage);
		}

		function onSuccess(resp) {
			var i;
			var from = resp.offset;
			var to = resp.offset + resp.count;
			data.length = parseInt(resp.total);

			for (i = 0; i < resp.logs.length; i++) {
				data[from + i] = resp.logs[i];
				data[from + i].index = from + i;
			}

			var message = {
				from : from,
				to : to,
				hosts : resp.hosts
			};
			if (req.autoScroll) {
				message.scrollTo = resp.position;
			}

			req = null;
			timeSelect = 0;

			onDataLoaded.notify(message);
		}

		function reloadData(from, to) {
			for ( var i = from; i <= to; i++)
				delete data[i];

			ensureData(from, to);
		}

		function setSearchOptions(searchOptions) {
			searchDateTime = searchOptions && searchOptions.searchDateTime
					|| "";
			levelThreshold = searchOptions && searchOptions.levelThreshold || 0;
			host = searchOptions && searchOptions.host || "";
			facility = searchOptions && searchOptions.facility || "";
			syslogTagPrefix = searchOptions && searchOptions.tagPrefix || "";
			allDays = searchOptions && searchOptions.allDays || "0";
			tabIndex = searchOptions && searchOptions.tabIndex || "0";
			clear();
		}

		init();

		return {
			// properties
			"data" : data,

			// methods
			"clear" : clear,
			"isDataLoaded" : isDataLoaded,
			"ensureData" : ensureData,
			"reloadData" : reloadData,
			"setSearchOptions" : setSearchOptions,

			// events
			"onDataLoading" : onDataLoading,
			"onDataLoaded" : onDataLoaded
		};
	}

	$.extend(true, window, {
		AjaxLogsBrowser: {
			SyslogRemoteModel : SyslogRemoteModel
		}
	});
})(jQuery);