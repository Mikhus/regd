Description
--------------------------------------------------------------------------------
RegD is a small library for Python which adds ability to trace decorators
and decorated functions in Python with meta-information. It work well with
both - Python 2.x and Python 3.x.

Nevertheless it was designed under Python 3, so it uses \_\_annotations\_\_
functions attribute specially introduced to store function meta.

It allows to trace your own and third-party decorators as well. All is required
is just to register any existing decorator with DecoratorRegistry, like

    from regd import DecoratorRegistry
    
    # create simple decorator which does nothing
    def mydecorator( fn) :
        # do your decorator stuff here...
        def wrapper( *args, **kwargs)
            # ... and here ... all you need
            return fn( *args, **kwargs)
        return wrapper
    
    # register the decorator
    mydecorator = DecoratorRegistry.decorator( mydecorator)

than just continue to use the decorator as usual:

    @mydecorator
    def mydecoratedfunction() :
        pass

Now any time you can easily track if function is decorated with decorator or
not, like:

    print(DecoratorRegistry.is_decorated_with(mydecoratedfunction, mydecorator))

Installation
--------------------------------------------------------------------------------
This module is availabe via Python Package Index (PyPI). Installation is
possible with pip or easy_install, like

    > pip install regd
or

    > easy_install regd

It's also available manual installation from git repository, like

    > git clone git://github.com/Mikhus/regd.git
    > cd regd
    > python setup.py install

Documentation
--------------------------------------------------------------------------------
RegD package documentation is available at http://packages.python.org/regd/

License
--------------------------------------------------------------------------------
This package is subject to MIT License. To get more info, please, see
LICENSE.txt file

Copyright (c) 2012
--------------------------------------------------------------------------------
Author: Mykhailo Stadnyk <mikhus@gmail.com>
Home page: https://github.com/Mikhus/regd
