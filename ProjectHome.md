Django ExtJS Connector

ExtJS Connector for Django

Currently only implements server side generation and validation of fields.

The extdjango/ directory in svn, is the proof-of-concept ext example i build to demonstrate server side generated and validated forms. Work on the real connector will start soon.

In the mean time if you want to checkout the extdjango example, change at least the following:
  * U have to move extdjango/extdjango.js to somewhere in your directory root
  * Change the templates extdjango/ to match your ExtJS and extdjango.js links
  * Change the hardcoded urls in extdjango.js, if u change the urls.