"""
This code is subject to MIT License

Copyright (c) 2012 Mykhailo Stadnyk <mikhus@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import types

class DecoratorRegistry( object) :
	"""
	Decorators registry.
	Adds tracking meta-info to the decorators and decorated functions and provides the API to
	work with it.
	
	Actually it makes possible to trace which function or class/object method decorated
	with each decorator. Sometimes it maybe really usefull to know.
	
	Registry works simply by registering the decorator before it's usage and after it's available
	to track the decorator usage. Here is a simple example:
	::
		from regd import DecoratorRegisrty
		
		# let's assume we have a decorator which do sume stuff and having name "cooldeco"
		# so we need only to register the decorator function with DecoratorRegistry
		cooldeco = DecoratorRegistry.decorator( cooldeco)
		
		# now we define a function which will be decorated with "cooldeco"
		@cooldeco
		def coolfunc() :
			# ... do something here ...
			return "I'm cool!"
		
		# Now at any place we can do, for example, such check
		if DecoratorRegistry.is_decorated_with( coolfunc, cooldeco) :
			# ... do something usefull ...
			print( "Yes, it is!")
		
	
	Current implementation does not use inspect module or code parsing, but have some rules and
	restrictions required to take into account:
	
	#. Only registered decorators are possible to track
	#. It's possible to track third-party decorators, them just required to be registered with
	   DecoratorRegistry **before** they are used
	#. Does not matter if registered decorator was used directly (f = d(f)) or by using syntax
	   sugar (@d) - it will work fine
	#. It is **not possible to register and track builtin decorators** like **staticmethod** or
	   **classmethod**.
	
	:Author: Mykhailo Stadnyk <mikhus@gmail.com>
	:Version: 1.3.1b
	"""
	
	NATIVE_FUNCTION = 'native_function'
	DECORATOR       = 'decorator'
	DECORATORS      = 'decorators'
	
	@classmethod
	def _make_portable( this, fn):
		""" Private method """
		if not hasattr( fn, '__annotations__'):
			setattr( fn, '__annotations__', {})
		
		return fn

	@classmethod
	def _getfn( this, fn):
		""" Private method """
		if type( fn) in [staticmethod, classmethod] :
			fn = fn.__func__
		return this._make_portable( fn)

	@classmethod
	def _set_native_function( this, fn, native_fn) :
		""" Private method """
		fn = this._getfn( fn)
		fn.__annotations__[this.NATIVE_FUNCTION] = native_fn

	@classmethod
	def _get_native_function( this, fn) :
		""" Private method """
		native_fn = this._getfn( fn)
		
		while this.NATIVE_FUNCTION in native_fn.__annotations__ :
			native_fn = native_fn.__annotations__[this.NATIVE_FUNCTION]
		
		return native_fn
	
	@classmethod
	def _set_decorator( this, fn, decorator) :
		""" Private method """
		fn = this._getfn( fn)
		fn.__annotations__[this.DECORATOR] = decorator
	
	@classmethod
	def _get_decorator( this, fn) :
		""" Private method """
		fn = this._getfn( fn)
		decorator = None
		
		if this.DECORATOR in fn.__annotations__ :
			decorator = fn.__annotations__[this.DECORATOR]
		
		return decorator
	
	@classmethod
	def _append_decorator( this, fn, decorator):
		""" Private method """
		native_fn = this._get_native_function( fn)
		
		if this.DECORATORS not in native_fn.__annotations__ :
			native_fn.__annotations__[this.DECORATORS] = []
		
		if decorator not in native_fn.__annotations__[this.DECORATORS]:
			native_fn.__annotations__[this.DECORATORS] += [decorator]
	
	@classmethod
	def get_real_function( this, fn):
		"""Returns the reference to the real function which was decorated
		and bypasses as fn argument to this method
		
		:param fn: function which was decorated
		:return: function - reference to the real function decorated with registered decorators 
		"""
		return this._get_native_function(fn)
	
	@classmethod
	def get_decorators( this, fn) :
		"""Returns list of registered decorators for the given function
		
		Usage example:
		::
			from regd import DecoratorRegisrty
			
			# defining decorator function
			def my_decorator( fn) :
				def wrapper( *args, **kwargs) :
					print( "%s called" %fn.__name__)
					return fn( *args, **kwargs)
				return wrapper
			
			# registering decorator function with DecoratorRegistry
			my_decorator = DecoratorRegistry.decorator( my_decorator)
			
			# defining decorated function
			@my_decorator
			def myfunc() : pass
			
			print( DecoratorRegistry.get_decorators( myfunc))
		
		:param fn: function to extract the decorators
		:rtype: list of dict {decoratorname : decoratorfunction} contains found decorators
		"""
		native_fn = this._get_native_function( fn)
		decorators = []
		
		if this.DECORATORS in native_fn.__annotations__ :
			decorators = native_fn.__annotations__[this.DECORATORS]
		
		return decorators
	
	@classmethod
	def decorator( this, native_decorator) :
		"""Register primitive decorator
		The primitive decorator is a decorator is a usual decorator which takes only decorating
		function as an argument
		Actually this method creates the new decorator function which is intended
		to replace the given native one. The new function do only the call of a native
		one but add registry meta-info to all decorator stuff
		
		Usage example:
		::
			from regd import DecoratorRegisrty
			
			# defining decorator function
			def my_decorator( fn) :
				def wrapper( *args, **kwargs) :
					print( "%s called" %fn.__name__)
					return fn( *args, **kwargs)
				return wrapper
			
			# registering decorator function with DecoratorRegistry
			my_decorator = DecoratorRegistry.decorator( my_decorator)
		
		:param native_decorator: real decorator function to register
		:rtype: new decorator function to replace the native one 
		"""
		def new_decorator( fn) :
			fn_decorator = native_decorator( fn)
			native_fn    = this._get_native_function( fn)
			
			this._set_decorator( fn_decorator, new_decorator)
			this._set_native_function( fn_decorator, native_fn)
			this._set_native_function( new_decorator, native_fn)
			this._append_decorator( native_fn, new_decorator)
			
			return fn_decorator
		
		new_decorator.__name__ = native_decorator.__name__
		new_decorator.__doc__  = native_decorator.__doc__
		
		return new_decorator
	
	@classmethod
	def parametrized_decorator( this, native_parametrized_decorator) :
		"""Register parametrized decorator
		The parametrized decorator is a decorator which is able to take an arguments
		So it looks like @mydecorator(param1=True,param2=False)
		When it is required to register parametrized decorator function this
		method should be used instead of DecoratorRegistry:decorator()
		Actually this method creates the new decorator function which is intended
		to replace the given native one. The new function do only the call of a native
		one but add registry meta-info to all decorator stuff
		
		Usage example:
		::
			from regd import DecoratorRegisrty
			
			# defining parametrized decorator function
			def my_decorator( *dargs, **dkwargs) :
				# ...
				# do some stuff with decorator arguments passed as *dargs, **dkwargs
				# ...
				# define a function decorator
				def decorator( fn) :
					def wrapper( *args, **kwargs) :
						print( "%s called" %fn.__name__)
						return fn( *args, **kwargs)
					return wrapper
				return decorator
			
			# registering decorator function with DecoratorRegistry
			my_decorator = DecoratorRegistry.parametrized_decorator( my_decorator)
		
		:param native_parametrized_decorator: real decorator function to register
		:rtype: new parametrized decorator function to replace the native one 
		"""
		def new_parametrized_decorator( *args, **kw) :
			native_decorator = native_parametrized_decorator( *args, **kw)
			
			def new_decorator( fn) :
				fn_decorator = native_decorator( fn)
				native_fn    = this._get_native_function( fn)
				
				this._set_decorator( fn_decorator, new_decorator)
				this._set_native_function( fn_decorator, native_fn)
				this._set_native_function( new_parametrized_decorator, native_fn)
				this._append_decorator( native_fn, new_parametrized_decorator)
				
				return fn_decorator
				
			new_decorator.__name__ = native_decorator.__name__
			new_decorator.__doc__  = native_decorator.__doc__
			
			return new_decorator
		
		new_parametrized_decorator.__name__ = native_parametrized_decorator.__name__
		new_parametrized_decorator.__doc__  = native_parametrized_decorator.__doc__
		
		return new_parametrized_decorator
	
	@classmethod
	def is_decorated_with( this, fn, decorator) :
		"""Checks if a given function decorated with the given decorator
		
		Usage example:
		::
			from regd import DecoratorRegisrty
			
			# defining decorator function
			def my_decorator( fn) :
				def wrapper( *args, **kwargs) :
					print( "%s called" %fn.__name__)
					return fn( *args, **kwargs)
				return wrapper
			
			# registering decorator function with DecoratorRegistry
			my_decorator = DecoratorRegistry.decorator( my_decorator)
			
			# example class
			class MyClass :
				@my_decorator
				def my_method( self) :
					if (DecoratorRegistry.is_decorated_with( self.my_method, my_decorator)) :
						print( "my_method is decorated with my_decorator" %())
					else :
						print( "my_method is not decorated with my_decorator")
			
			inst = MyClass()
			inst.my_method()
		
		:param fn: function to check
		:param decorator: decorator function to check with
		:rtype: bool  
		"""
		return decorator in  this.get_decorators( fn)
	
	@classmethod
	def decorated_methods( this, cls, decorator) :
		"""Returns generator for all found methods decorated with given decorator in a given class
		
		Usage example:
		::
			from regd import DecoratorRegisrty
			
			# defining decorator function
			def my_decorator( fn) :
				def wrapper( *args, **kwargs) :
					print( "%s called" %fn.__name__)
					return fn( *args, **kwargs)
				return wrapper
			
			# registering decorator function with DecoratorRegistry
			my_decorator = DecoratorRegistry.decorator( my_decorator)
			
			# example class
			class MyClass :
				@my_decorator
				def my_method( self) :
					pass
				
				@my_decorator
				def my_internal_call( self) :
					print( "Internal class lookup result:")
					print( list( DecoratorRegistry.decorated_methods( self, my_decorator)))
			
			print( "External class lookup result:")
			print( list( DecoratorRegistry.decorated_methods( MyClass, my_decorator)))
			
			inst = MyClass()
			inst.my_internal_call()
		
		:param cls: class or object to search
		:param decorator: decorator function to search
		:rtype: generator of dict {methodname : method} contains found decorated class methods 
		"""
		# lookup for class in given cls parameter. All the class objects have type 'type'
		while cls.__class__ is not type :
			cls = cls.__class__
		
		# search for decorated methods
		for methodname in cls.__dict__.keys() :
			method = cls.__dict__[methodname]
			if type( method) is types.FunctionType :
				if decorator in this.get_decorators( method) :
					yield { methodname : method }
	
	@classmethod
	def all_decorated_module_functions( this, module, exclude_methods = False, exclude_functions = False) :
		"""Returns generator of functions decorated with any registered decorator
		in a given module.

		By defualt it will find all functions and class methods.

		*NOTE: only **registered** decorators are taken into account while searching the module. So it means
		taht you need to register all the decorators which are used in a given module
		before module import is done. Or registration of decorators should be done inside
		the module before their actual use.*
		
		Usage example:
		::
			from regd import DecoratorRegisrty

			# import the module containing decorators definition 
			import somedecomodule
			
			# register the decorators
			somedecomodule.deco1 = DecoratorRegistry.decorator( deco1)
			somedecomodule.deco2 = DecoratorRegistry.parametrized_decorator( deco2)
			
			# now import the module where deco1 and deco2 should be actually used
			# to decorate the functions/methods
			import somemodule
			
			# now we can trace all registered decorators usage in a module like:
			print( "All decorated functions/methods in a module are:")
			print( list( DecoratorRegistry.all_decorated_module_functions( somemodule)))
		
		:param module: module to lookup for decorated functions
		:param exclude_methods: bool flag to turn on/off class method inclusion into result
		:param exclude_functions: bool flag to turn on/off function inclusion into result
		:rtype: generator of dict { function_name : function }
		"""
		module_names = []
		for el in dir( module) :
			fn = module.__dict__.get( el)

			# lookup for functions
			if not exclude_functions and type( fn) in [types.FunctionType, staticmethod, classmethod] :
				fn = this._getfn( fn)
				if len( this.get_decorators( fn)) > 0 :
					fname = fn.__annotations__[this.NATIVE_FUNCTION].__name__
					if fname not in module_names :
						yield { fname : module.__dict__.get( fname) }
						module_names += [fname]
			
			# lookup for class methods
			if not exclude_methods and type( fn) is type :
				for cls_el in dir( fn) :
					method = fn.__dict__.get( cls_el)
					if type( method) in [types.FunctionType, staticmethod, classmethod] :
						method = this._getfn( method)
						if len( this.get_decorators( method)) > 0:
							fname = method.__annotations__[this.NATIVE_FUNCTION].__name__
							if fname not in module_names :
								yield { "%s.%s" %(fn.__name__, fname) : fn.__dict__.get( fname) }
								module_names += [fname]
	
	@classmethod
	def module_functions_decorated_with( this, module, decorator, exclude_methods = False, exclude_functions = False) :
		"""Returns generator of functions decorated with a given registered decorator
		in a given module.

		By default it will find all functions and class methods.
		
		*NOTE: only **registered** decorators are taken into account while searching the module. So it means
		taht you need to register all the decorators which are used in a given module
		before module import is done. Or registration of decorators should be done inside
		the module before their actual use.*
		
		Usage example:
		::
			from regd import DecoratorRegisrty

			# import the module containing decorators definition 
			import somedecomodule
			
			# register the decorators
			somedecomodule.deco1 = DecoratorRegistry.decorator( deco1)
			somedecomodule.deco2 = DecoratorRegistry.parametrized_decorator( deco2)
			
			# now import the module where deco1 and deco2 should be actually used
			# to decorate the functions/methods
			import somemodule
			
			# now we can trace decorators usage in a module like:
			print( "deco1 is applied to:")
			print( list( DecoratorRegistry.module_functions_decorated_with( somemodule, somedecomodule.deco1)))
			
			print( "deco2 is applied to:")
			print( list( DecoratorRegistry.module_functions_decorated_with( somemodule, somedecomodule.deco2)))
		
		:param module: module to lookup for decorated functions
		:param decorator: function which is used as decorator
		:param exclude_methods: bool flag to turn on/off class method inclusion into result
		:param exclude_functions: bool flag to turn on/off function inclusion into result
		:rtype: generator of dict { function_name : function }
		"""
		for mfn in this.all_decorated_module_functions( module, exclude_methods, exclude_functions) :
			for fname, fn in mfn.items() :
				if decorator in this.get_decorators( fn) :
					yield { fname : fn }

if __name__ == "__main__" :
	"""	Performing unit tests for the DecoratorRegistry functionality """
	import unittest

	try :
		from regd.test import TestDecoratorRegistry
	except ImportError :
		import os, sys
		sys.path.insert( 0, "%s/.." %os.getcwd())
		from regd.test import TestDecoratorRegistry

	suite = unittest.TestLoader().loadTestsFromTestCase( TestDecoratorRegistry)
	unittest.TextTestRunner( verbosity = 2).run( suite)
