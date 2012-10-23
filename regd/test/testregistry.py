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

Unit tests for decorator registry module

@author: Mykhailo Stadnyk <mikhus@gmail.com>
@version: 1.3.1b
"""
import unittest
from regd import DecoratorRegistry

"""Decorator which will be never registered
"""
def free_decorator( fn) :
	def wrapper( *args, **kwargs) :
		return fn( *args, **kwargs)
	return wrapper

"""Primitive decorator to deal with
"""
def just_decorator( fn) :
	def wrapper( *args, **kwargs) :
		return fn( *args, **kwargs)
	return wrapper

"""Parametrized decorator to deal with
"""
def decorator_with_args( *dargs, **dkwargs) :
	def decorator( fn) :
		def wrapper( *args, **kwargs) :
			return fn( *args, **kwargs)
		return wrapper
	return decorator

class TestDecoratorRegistry( unittest.TestCase) :

	def setUp( self) :
		unittest.TestCase.setUp( self)

	def test1_make_portable( self) :
		def somefunc() : pass
		DecoratorRegistry._make_portable( somefunc)
		self.assertTrue( hasattr( somefunc, '__annotations__'))

	def test2_decorator( self) :
		@just_decorator
		def somefunc( *args) : return args
		noregres = somefunc( 7, 7, 7)

		rjd = DecoratorRegistry.decorator( just_decorator)
		@rjd
		def somefunc2( *args) : return args
		regres = somefunc2( 7, 7, 7)

		self.assertEqual( noregres, regres)
		self.assertTrue( DecoratorRegistry.DECORATOR in somefunc2.__annotations__)
		self.assertTrue( DecoratorRegistry.NATIVE_FUNCTION in somefunc2.__annotations__)
		self.assertEqual( somefunc2.__annotations__[DecoratorRegistry.NATIVE_FUNCTION].__name__, 'somefunc2')
		self.assertTrue( DecoratorRegistry.DECORATORS in somefunc2.__annotations__[DecoratorRegistry.NATIVE_FUNCTION].__annotations__)
		self.assertTrue( rjd in somefunc2.__annotations__[DecoratorRegistry.NATIVE_FUNCTION].__annotations__[DecoratorRegistry.DECORATORS])

	def test3_parametrized_decorator( self) :
		@decorator_with_args(1, 2, 3)
		def somefunc( *args) : return args
		noregres = somefunc( 7, 7, 7)

		rdwa = DecoratorRegistry.parametrized_decorator( decorator_with_args)
		@rdwa(1, 2, 3)
		def somefunc2( *args) : return args
		regres = somefunc2( 7, 7, 7)

		self.assertEqual( noregres, regres)
		self.assertTrue( DecoratorRegistry.DECORATOR in somefunc2.__annotations__)
		self.assertTrue( DecoratorRegistry.NATIVE_FUNCTION in somefunc2.__annotations__)
		self.assertEqual( somefunc2.__annotations__[DecoratorRegistry.NATIVE_FUNCTION].__name__, 'somefunc2')
		self.assertTrue( DecoratorRegistry.DECORATORS in somefunc2.__annotations__[DecoratorRegistry.NATIVE_FUNCTION].__annotations__)
		self.assertTrue( rdwa in somefunc2.__annotations__[DecoratorRegistry.NATIVE_FUNCTION].__annotations__[DecoratorRegistry.DECORATORS])

	def test4_is_decorated_with( self) :
		@decorator_with_args(1, 2, 3)
		def somefunc10( *args) : return args
		rdwa = DecoratorRegistry.parametrized_decorator( decorator_with_args)
		@rdwa(1, 2, 3)
		def somefunc20( *args) : return args
		
		@just_decorator
		def somefunc30( *args) : return args
		rjd = DecoratorRegistry.decorator( just_decorator)
		@rjd
		def somefunc40( *args) : return args

		self.assertFalse( DecoratorRegistry.is_decorated_with( somefunc10, decorator_with_args))
		self.assertTrue( DecoratorRegistry.is_decorated_with( somefunc20, rdwa))
		self.assertFalse( DecoratorRegistry.is_decorated_with( somefunc30, just_decorator))
		self.assertTrue( DecoratorRegistry.is_decorated_with( somefunc40, rjd))
	
	def test5_decorated_methods( self) :
		dwa = DecoratorRegistry.parametrized_decorator( decorator_with_args)
		jd = DecoratorRegistry.decorator( decorator_with_args)
		
		class TestClass( object):
			@jd
			@dwa(1, 2, 3)
			@free_decorator
			def test_method( self) :
				pass
		
		self.assertTrue( 'test_method' in next( DecoratorRegistry.decorated_methods( TestClass, jd)))
		self.assertTrue( 'test_method' in next( DecoratorRegistry.decorated_methods( TestClass, dwa)))
		self.assertFalse( len( list( DecoratorRegistry.decorated_methods( TestClass, free_decorator))) != 0)

	def test6_get_decorators( self) :
		from . import testmodule
		
		decos = DecoratorRegistry.get_decorators( testmodule.non_class_member)

		self.assertTrue( testmodule.deco in decos)
		self.assertTrue( testmodule.deco2 in decos)
		self.assertEqual( len( decos), 2)
	
	def test7_all_decorated_module_functions( self) :
		from . import testmodule
		funcs = list( DecoratorRegistry.all_decorated_module_functions( testmodule))
		self.assertEqual( len( funcs), 3)
	
	def test8_module_functions_decorated_with( self) :
		from . import testmodule
		funcs = list( DecoratorRegistry.module_functions_decorated_with( testmodule, testmodule.deco2))
		self.assertEqual( len( funcs), 2)
		
