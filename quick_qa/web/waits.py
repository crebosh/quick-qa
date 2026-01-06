class DocumentReady:
    def __call__(self, driver):
        return driver.execute_script("return document.readyState") == "complete"


class JQueryInactive:
    def __call__(self, driver):
        return driver.execute_script(
            """
            return window.jQuery === undefined || jQuery.active === 0;
        """
        )


class NetworkIdle:
    def __init__(self):
        self._script = """
        if (!window.__seleniumXHRTracker) {
            window.__seleniumXHRTracker = { pending: 0 };

            const open = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function() {
                this.addEventListener('readystatechange', function() {
                    if (this.readyState === 1) window.__seleniumXHRTracker.pending++;
                    if (this.readyState === 4) window.__seleniumXHRTracker.pending--;
                });
                open.apply(this, arguments);
            };

            const fetch = window.fetch;
            window.fetch = function() {
                window.__seleniumXHRTracker.pending++;
                return fetch.apply(this, arguments).finally(() => {
                    window.__seleniumXHRTracker.pending--;
                });
            };
        }
        return window.__seleniumXHRTracker.pending;
        """

    def __call__(self, driver):
        return driver.execute_script(self._script) == 0
