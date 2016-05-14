#
# Copyright (c) 2012-2015 Codenvy, S.A.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#   Codenvy, S.A. - initial API and implementation
#

FROM codenvy/python27_gae
EXPOSE 8000 8080
ENV CODENVY_APP_PORT_8000_HTTP 8000
ENV CODENVY_APP_PORT_8080_HTTP 8080
ENV CODENVY_APP_BIND_DIR /home/user/app
VOLUME ["/home/user/app"]
CMD /home/user/google_appengine/dev_appserver.py 2>&1 --host 0.0.0.0 --admin_host=0.0.0.0 --skip_sdk_update_check true /home/user/app
