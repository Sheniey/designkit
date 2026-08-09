use pyo3::exceptions::{
    PyAssertionError,
    PyAttributeError,
    PyTypeError,
    PyValueError,
    PyTimeoutError,
};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict, PyModule, PyTuple, PyType};
use std::ffi::CString;


// ============================================================
// Python helpers
// ============================================================
//
// Los métodos async se implementan como coroutines Python reales.
// Esto evita necesitar tokio/pyo3-async-runtimes solamente para
// conservar la semántica de tu implementación original.
// ============================================================

const ASYNC_HELPERS: &str = r#"
import asyncio
import time


async def _return_async(target, args, kwargs, async_fn, return_type):
    if not callable(target):
        return False

    try:
        if async_fn:
            result = await target(*args, **kwargs)
        else:
            result = target(*args, **kwargs)
    except Exception:
        return False

    return isinstance(result, return_type)


async def _raise_async(target, args, kwargs, async_fn, exception):
    if not callable(target):
        return False

    try:
        if async_fn:
            await target(*args, **kwargs)
        else:
            target(*args, **kwargs)
    except exception:
        return True
    except Exception:
        return False

    return False


async def _assert_async_return(
    target,
    args,
    kwargs,
    async_fn,
    return_type,
    self_obj,
    message,
):
    ok = await _return_async(
        target,
        args,
        kwargs,
        async_fn,
        return_type,
    )

    if not ok:
        raise AssertionError(message)

    return self_obj


async def _must_async_return(
    target,
    args,
    kwargs,
    async_fn,
    return_type,
    custom_expt,
    message,
):
    ok = await _return_async(
        target,
        args,
        kwargs,
        async_fn,
        return_type,
    )

    if not ok:
        raise custom_expt(message)

    return None


async def _assert_async_raise(
    target,
    args,
    kwargs,
    async_fn,
    exception,
    self_obj,
    message,
):
    ok = await _raise_async(
        target,
        args,
        kwargs,
        async_fn,
        exception,
    )

    if not ok:
        raise AssertionError(message)

    return self_obj


async def _must_async_raise(
    target,
    args,
    kwargs,
    async_fn,
    exception,
    custom_expt,
):
    try:
        if async_fn:
            await target(*args, **kwargs)
        else:
            target(*args, **kwargs)

    except exception:
        return None

    except Exception as e:
        raise custom_expt(
            f"Object async {target} raised {type(e)} instead of {exception}"
        )

    raise custom_expt(
        f"Object async {target} did not raise any exception, expected {exception}"
    )


async def _should_async_run_within(
    target,
    args,
    kwargs,
    async_fn,
    time_limit,
):
    start_time = time.perf_counter()

    try:
        if async_fn:
            await asyncio.wait_for(
                target(*args, **kwargs),
                timeout=time_limit,
            )
        else:
            target(*args, **kwargs)

    except asyncio.TimeoutError:
        return False

    end_time = time.perf_counter()

    return (end_time - start_time) < time_limit


async def _assert_async_run_within(
    target,
    args,
    kwargs,
    async_fn,
    time_limit,
    self_obj,
    message,
):
    start_time = time.perf_counter()

    try:
        if async_fn:
            await asyncio.wait_for(
                target(*args, **kwargs),
                timeout=time_limit,
            )
        else:
            target(*args, **kwargs)

    except asyncio.TimeoutError:
        raise AssertionError(message)

    end_time = time.perf_counter()

    if not ((end_time - start_time) < time_limit):
        raise AssertionError(message)

    return self_obj


async def _must_async_run_within(
    target,
    args,
    kwargs,
    async_fn,
    time_limit,
    custom_expt,
    message,
):
    start_time = time.perf_counter()

    try:
        if async_fn:
            await asyncio.wait_for(
                target(*args, **kwargs),
                timeout=time_limit,
            )
        else:
            target(*args, **kwargs)

    except asyncio.TimeoutError:
        raise custom_expt(message)

    end_time = time.perf_counter()

    if not ((end_time - start_time) < time_limit):
        raise custom_expt(message)

    return None
"#;


// ============================================================
// Helpers Rust / PyO3
// ============================================================

fn async_helper_module<'py>(
    py: Python<'py>,
) -> PyResult<Bound<'py, PyModule>> {
    let code = CString::new(ASYNC_HELPERS)
        .expect("ASYNC_HELPERS cannot contain NUL bytes");

    PyModule::from_code(
        py,
        code.as_c_str(),
        c"designkit_async.py",
        c"designkit_async",
    )
}

fn async_helper_call<'py>(
    py: Python<'py>,
    name: &str,
    args: Bound<'py, PyTuple>,
) -> PyResult<Bound<'py, PyAny>> {
    let module = async_helper_module(py)?;
    let function = module.getattr(name)?;

    function.call1(args)
}


fn classname_bound(
    obj: &Bound<'_, PyAny>,
) -> PyResult<String> {
    let py = obj.py();
    let inspect = py.import("inspect")?;

    let is_function =
        inspect
            .getattr("isfunction")?
            .call1((obj,))?
            .extract::<bool>()?;

    let is_method =
        inspect
            .getattr("ismethod")?
            .call1((obj,))?
            .extract::<bool>()?;

    if is_function || is_method {
        let qualname: String =
            obj.getattr("__qualname__")?.extract()?;

        return Ok(
            qualname
                .split('.')
                .next()
                .unwrap_or(&qualname)
                .to_owned()
        );
    }

    let is_class =
        inspect
            .getattr("isclass")?
            .call1((obj,))?
            .extract::<bool>()?;

    if is_class {
        return obj.getattr("__name__")?.extract();
    }

    obj.get_type()
        .getattr("__name__")?
        .extract()
}


fn default_exception_type<'py>(
    py: Python<'py>,
    exception: &'static str,
) -> PyResult<Bound<'py, PyType>> {
    let builtins = py.import("builtins")?;
    let value = builtins.getattr(exception)?;

    Ok(value.cast::<PyType>()?.clone())
}


fn raise_custom(
    custom_expt: Bound<'_, PyType>,
    message: String,
) -> PyResult<()> {
    Err(PyErr::from_type(custom_expt, message))
}


fn clone_assertion(
    py: Python<'_>,
    assertion: &Assertion,
) -> PyResult<Py<Assertion>> {
    Py::new(
        py,
        Assertion {
            target: assertion.target.clone_ref(py),
            target_kind: assertion.target_kind.clone(),
            async_fn: assertion.async_fn,
            args: assertion.args.clone_ref(py),
            kwargs: assertion.kwargs.clone_ref(py),
        },
    )
}



// ============================================================
// Assertion
// ============================================================

#[pyclass]
struct Assertion {
    target: Py<PyAny>,

    target_kind: String,

    async_fn: bool,

    args: Py<PyTuple>,

    kwargs: Py<PyDict>,
}


#[pymethods]
impl Assertion {

    // ========================================================
    // __init__
    // ========================================================

    #[new]
    #[pyo3(signature = (target, *args, **kwargs))]
    fn new(
        py: Python<'_>,
        target: Py<PyAny>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Self> {
        let target_bound = target.bind(py);

        let inspect = py.import("inspect")?;

        let target_kind =
            if inspect
                .getattr("isclass")?
                .call1((target_bound,))?
                .extract::<bool>()?
            {
                "class"
            }
            else if target_bound.is_callable() {
                "function"
            }
            else {
                "object"
            };


        let is_coroutine =
            inspect
                .getattr("iscoroutinefunction")?
                .call1((target_bound,))?
                .extract::<bool>()?;

        let is_async_generator =
            inspect
                .getattr("isasyncgenfunction")?
                .call1((target_bound,))?
                .extract::<bool>()?;

        let async_fn =
            is_coroutine || is_async_generator;


        let kwargs_obj = match kwargs {
            Some(value) => value.copy()?.unbind(),
            None => PyDict::new(py).unbind(),
        };


        Ok(Self {
            target,
            target_kind: target_kind.to_owned(),
            async_fn,
            args: args.clone().unbind(),
            kwargs: kwargs_obj,
        })
    }


    // ========================================================
    // repr / str
    // ========================================================

    fn __repr__(
        &self,
        py: Python<'_>,
    ) -> PyResult<String> {
        let target =
            self.target.bind(py).repr()?;

        Ok(format!(
            "Assertion( {} )",
            target
        ))
    }


    fn __str__(
        &self,
        py: Python<'_>,
    ) -> PyResult<String> {
        self.__repr__(py)
    }


    // ========================================================
    // VOID
    // ========================================================

    fn _be_void(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        let target =
            self.target.bind(py);

        // Conservamos exactamente la lógica Python:
        //
        // self.__target is not None or not self.__target

        Ok(
            !target.is_none()
                || !target.is_truthy()?
        )
    }


    fn assert_be_void(
        &self,
        py: Python<'_>,
        message: String,
    ) -> PyResult<Py<Assertion>> {
        if !self._be_void(py)? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (*, custom_expt = None))]
    fn must_be_void(
        &self,
        py: Python<'_>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._be_void(py)? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "ValueError",
                        )?,
                };

            let message = format!(
                "Object {} is None or empty",
                self.target.bind(py).repr()?
            );

            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    fn should_be_void(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        self._be_void(py)
    }


    // ========================================================
    // BE
    // ========================================================

    fn _be(
        &self,
        py: Python<'_>,
        types: &Bound<'_, PyTuple>,
    ) -> PyResult<bool> {
        let target =
            self.target.bind(py);


        // ----------------------------------------------------
        // Filter None
        // ----------------------------------------------------

        let filtered: Vec<Bound<'_, PyAny>> =
            types
                .iter()
                .filter(|t| !t.is_none())
                .collect();


        // Igual que:
        //
        // if len(fil_types) < len(types)
        // and self.__target is None:
        //     return True

        if filtered.len() < types.len()
            && target.is_none()
        {
            return Ok(true);
        }


        let builtins =
            py.import("builtins")?;


        // ----------------------------------------------------
        // 1. isinstance
        // ----------------------------------------------------

        for expected in &filtered {
            let result =
                builtins
                    .getattr("isinstance")?
                    .call1((
                        target,
                        expected,
                    ))?
                    .extract::<bool>()?;

            if result {
                return Ok(true);
            }
        }


        // ----------------------------------------------------
        // 2. issubclass(type(target), expected)
        // ----------------------------------------------------

        let target_type =
            target.get_type();

        for expected in &filtered {
            let result =
                builtins
                    .getattr("issubclass")?
                    .call1((
                        &target_type,
                        expected,
                    ))?
                    .extract::<bool>()?;

            if result {
                return Ok(true);
            }
        }


        // ----------------------------------------------------
        // 3. attribute comparison
        // ----------------------------------------------------
        //
        // Conservamos tu comportamiento original:
        //
        // getattr(target, '__dict__', None)
        // and not any(
        //     hasattr(target, attr)
        //     for attr in dir(target)
        //     if not attr.startswith('__')
        // )
        //
        // Es deliberadamente "weird", como comentaste.
        // ----------------------------------------------------

        if let Ok(dict) =
            target.getattr("__dict__")
        {
            if dict.is_truthy()? {
                let attributes =
                    target.call_method0("__dir__")?;

                for attr in attributes.try_iter()? {
                    let attr = attr?;

                    let name: String =
                        attr.extract()?;

                    if name.starts_with("__") {
                        continue;
                    }

                    if target.hasattr(&name)? {
                        return Ok(false);
                    }
                }

                return Ok(true);
            }
        }


        Ok(false)
    }


    #[pyo3(signature = (message, *types))]
    fn assert_be(
        slf: PyRef<'_, Self>,
        py: Python<'_>,
        message: String,
        types: &Bound<'_, PyTuple>,
    ) -> PyResult<Py<Assertion>> {
        if !slf._be(py, types)? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, &slf)?)
    }


    #[pyo3(signature = (*types, custom_expt = None))]
    fn must_be(
        &self,
        py: Python<'_>,
        types: &Bound<'_, PyTuple>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._be(py, types)? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "TypeError",
                        )?,
                };


            let names =
                types
                    .iter()
                    .filter(|t| !t.is_none())
                    .map(|t| classname_bound(&t))
                    .collect::<PyResult<Vec<_>>>()?
                    .join(", ");


            let message = format!(
                "Object {} is not one of the following types {}",
                self.target.bind(py).repr()?,
                names
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    #[pyo3(signature = (*types))]
    fn should_be(
        &self,
        py: Python<'_>,
        types: &Bound<'_, PyTuple>,
    ) -> PyResult<bool> {
        self._be(py, types)
    }


    // ========================================================
    // HAVE
    // ========================================================

    fn _have(
        &self,
        py: Python<'_>,
        attributes: &Bound<'_, PyTuple>,
    ) -> PyResult<(bool, Vec<String>)> {
        let target =
            self.target.bind(py);

        let mut missing =
            Vec::new();


        for attr in attributes.iter() {
            let name: String =
                attr.extract()?;

            if !target.hasattr(&name)? {
                missing.push(name);
            }
        }


        Ok((
            missing.is_empty(),
            missing,
        ))
    }


    #[pyo3(signature = (message, *attributes))]
    fn assert_have(
        slf: PyRef<'_, Self>,
        py: Python<'_>,
        message: String,
        attributes: &Bound<'_, PyTuple>,
    ) -> PyResult<Py<Assertion>> {
        let (ok, _) =
            slf._have(py, attributes)?;

        if !ok {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, &slf)?)
    }


    #[pyo3(signature = (*attributes, custom_expt = None))]
    fn must_have(
        &self,
        py: Python<'_>,
        attributes: &Bound<'_, PyTuple>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        let (ok, missing) =
            self._have(py, attributes)?;

        if !ok {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "AttributeError",
                        )?,
                };


            let message = format!(
                "Object {} does not have attributes {:?}",
                self.target.bind(py).repr()?,
                missing
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    #[pyo3(signature = (*attributes))]
    fn should_have(
        &self,
        py: Python<'_>,
        attributes: &Bound<'_, PyTuple>,
    ) -> PyResult<bool> {
        Ok(
            self._have(
                py,
                attributes,
            )?.0
        )
    }


    // ========================================================
    // IMPLEMENT
    // ========================================================

    fn _implement(
        &self,
        py: Python<'_>,
        methods: &Bound<'_, PyTuple>,
    ) -> PyResult<(bool, Vec<String>)> {
        let target =
            self.target.bind(py);

        let mut missing =
            Vec::new();


        for method in methods.iter() {
            let name =
                if method.is_callable() {
                    method
                        .getattr("__name__")?
                        .extract::<String>()?
                } else {
                    method.extract::<String>()?
                };


            let callable =
                match target.getattr(&name) {
                    Ok(value) =>
                        value.is_callable(),
                    Err(_) =>
                        false,
                };


            if !callable {
                missing.push(name);
            }
        }


        Ok((
            missing.is_empty(),
            missing,
        ))
    }


    #[pyo3(signature = (message, *methods))]
    fn assert_implement(
        &self,
        py: Python<'_>,
        message: String,
        methods: &Bound<'_, PyTuple>,
    ) -> PyResult<Py<Assertion>> {
        let (ok, _) =
            self._implement(
                py,
                methods,
            )?;

        if !ok {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (*methods, custom_expt = None))]
    fn must_implement(
        &self,
        py: Python<'_>,
        methods: &Bound<'_, PyTuple>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        let (ok, missing) =
            self._implement(
                py,
                methods,
            )?;

        if !ok {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "NotImplementedError",
                        )?,
                };


            let message = format!(
                "Object {} does not implement methods {:?}",
                self.target.bind(py).repr()?,
                missing
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    #[pyo3(signature = (*methods))]
    fn should_implement(
        &self,
        py: Python<'_>,
        methods: &Bound<'_, PyTuple>,
    ) -> PyResult<bool> {
        Ok(
            self._implement(
                py,
                methods,
            )?.0
        )
    }


    // ========================================================
    // INHERIT
    // ========================================================

    fn _inherit(
        &self,
        py: Python<'_>,
        base_classes: &Bound<'_, PyTuple>,
    ) -> PyResult<bool> {
        let inspect =
            py.import("inspect")?;

        let target =
            self.target.bind(py);


        let cls =
            if inspect
                .getattr("isclass")?
                .call1((target,))?
                .extract::<bool>()?
            {
                target.clone()
            } else {
                target.get_type().into_any()
            };


        let builtins =
            py.import("builtins")?;


        for base in base_classes.iter() {
            let result =
                builtins
                    .getattr("issubclass")?
                    .call1((
                        &cls,
                        &base,
                    ))?
                    .extract::<bool>()?;

            if result {
                return Ok(true);
            }
        }


        Ok(false)
    }


    #[pyo3(signature = (message, *base_classes))]
    fn assert_inherit(
        &self,
        py: Python<'_>,
        message: String,
        base_classes: &Bound<'_, PyTuple>,
    ) -> PyResult<Py<Assertion>> {
        if !self._inherit(
            py,
            base_classes,
        )? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (*base_classes, custom_expt = None))]
    fn must_inherit(
        &self,
        py: Python<'_>,
        base_classes: &Bound<'_, PyTuple>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._inherit(
            py,
            base_classes,
        )? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "TypeError",
                        )?,
                };


            let message = format!(
                "Object {} does not inherit from {:?}",
                self.target.bind(py).repr()?,
                base_classes
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    #[pyo3(signature = (*base_classes))]
    fn should_inherit(
        &self,
        py: Python<'_>,
        base_classes: &Bound<'_, PyTuple>,
    ) -> PyResult<bool> {
        self._inherit(
            py,
            base_classes,
        )
    }


    // ========================================================
    // RETURN
    // ========================================================

    fn _return(
        &self,
        py: Python<'_>,
        return_type: &Bound<'_, PyAny>,
    ) -> PyResult<bool> {
        if !self._be_callable(py)? {
            return Ok(false);
        }


        let target =
            self.target.bind(py);


        let result =
            match target.call(
                self.args.bind(py),
                Some(self.kwargs.bind(py)),
            ) {
                Ok(value) => value,
                Err(_) => return Ok(false),
            };


        py.import("builtins")?
            .getattr("isinstance")?
            .call1((
                result,
                return_type,
            ))?
            .extract()
    }


    #[pyo3(signature = (message, return_type))]
    fn assert_return(
        &self,
        py: Python<'_>,
        message: String,
        return_type: &Bound<'_, PyAny>,
    ) -> PyResult<Py<Assertion>> {
        if !self._return(
            py,
            return_type,
        )? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (return_type, custom_expt = None))]
    fn must_return(
        &self,
        py: Python<'_>,
        return_type: &Bound<'_, PyAny>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._return(
            py,
            return_type,
        )? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "TypeError",
                        )?,
                };


            let message = format!(
                "Object {} does not return {}",
                self.target.bind(py).repr()?,
                return_type.repr()?
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    fn should_return(
        &self,
        py: Python<'_>,
        return_type: &Bound<'_, PyAny>,
    ) -> PyResult<bool> {
        self._return(
            py,
            return_type,
        )
    }


    // ========================================================
    // RAISE
    // ========================================================

    fn _raise(
        &self,
        py: Python<'_>,
        exception: &Bound<'_, PyAny>,
    ) -> PyResult<bool> {
        let target =
            self.target.bind(py);


        match target.call(
            self.args.bind(py),
            Some(self.kwargs.bind(py)),
        ) {
            Ok(_) => Ok(false),

            Err(err) => {
                Ok(err.matches(py, exception)?)
            }
        }
    }


    #[pyo3(signature = (message, exception))]
    fn assert_raise(
        &self,
        py: Python<'_>,
        message: String,
        exception: &Bound<'_, PyAny>,
    ) -> PyResult<Py<Assertion>> {
        if !self._raise(
            py,
            exception,
        )? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (exception, custom_expt = None))]
    fn must_raise(
        &self,
        py: Python<'_>,
        exception: &Bound<'_, PyAny>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        let target = self.target.bind(py);

        let custom = match custom_expt {
            Some(value) => value,
            None => default_exception_type(py, "TypeError")?,
        };

        match target.call(
            self.args.bind(py),
            Some(self.kwargs.bind(py)),
        ) {
            Ok(_) => {
                let message = format!(
                    "Object {} did not raise any exception, expected {}",
                    target.repr()?,
                    exception.repr()?
                );

                raise_custom(custom, message)
            }

            Err(err) => {
                let matches = err.matches(py, exception)?;

                if matches {
                    return Ok(());
                }

                let actual = err.get_type(py);

                let message = format!(
                    "Object {} raised {} instead of {}",
                    target.repr()?,
                    actual.repr()?,
                    exception.repr()?
                );

                raise_custom(custom, message)
            }
        }
    }


    fn should_raise(
        &self,
        py: Python<'_>,
        exception: &Bound<'_, PyAny>,
    ) -> PyResult<bool> {
        self._raise(
            py,
            exception,
        )
    }


    // ========================================================
    // ASYNC
    // ========================================================

    fn _be_async(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        Ok(
            self._be_callable(py)?
                && self.async_fn
        )
    }


    fn assert_be_async(
        &self,
        py: Python<'_>,
        message: String,
    ) -> PyResult<Py<Assertion>> {
        if !self._be_async(py)? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (custom_expt = None))]
    fn must_be_async(
        &self,
        py: Python<'_>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._be_async(py)? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "TypeError",
                        )?,
                };


            let message = format!(
                "Object {} is not an async function or coroutine",
                self.target.bind(py).repr()?
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    fn should_be_async(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        self._be_async(py)
    }


    fn can_be_async(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        py.import("inspect")?
            .getattr("isawaitable")?
            .call1((
                self.target.bind(py),
            ))?
            .extract()
    }


    // ========================================================
    // CALLABLE
    // ========================================================

    fn _be_callable(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        Ok(
            self.target_kind == "function"
                || self.target_kind == "class"
                || self.target.bind(py).is_callable()
        )
    }


    fn assert_be_callable(
        &self,
        py: Python<'_>,
        message: String,
    ) -> PyResult<Py<Assertion>> {
        if !self._be_callable(py)? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (custom_expt = None))]
    fn must_be_callable(
        &self,
        py: Python<'_>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._be_callable(py)? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "TypeError",
                        )?,
                };


            let message = format!(
                "Object {} is not callable",
                self.target.bind(py).repr()?
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    fn should_be_callable(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        self._be_callable(py)
    }


    // ========================================================
    // ITERABLE
    // ========================================================

    fn _be_iterable(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        self.target
            .bind(py)
            .hasattr("__iter__")
    }


    fn assert_be_iterable(
        &self,
        py: Python<'_>,
        message: String,
    ) -> PyResult<Py<Assertion>> {
        if !self._be_iterable(py)? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (custom_expt = None))]
    fn must_be_iterable(
        &self,
        py: Python<'_>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._be_iterable(py)? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "TypeError",
                        )?,
                };


            let message = format!(
                "Object {} is not iterable",
                self.target.bind(py).repr()?
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    fn should_be_iterable(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        self._be_iterable(py)
    }


    // ========================================================
    // DOCUMENTED
    // ========================================================

    fn _be_documented(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        let inspect =
            py.import("inspect")?;

        let target =
            self.target.bind(py);


        if inspect
            .getattr("getdoc")?
            .call1((target,))?
            .is_truthy()?
        {
            return Ok(true);
        }


        if target
            .getattr("__doc__")?
            .is_truthy()?
        {
            return Ok(true);
        }


        match target.getattr("__annotations__") {
            Ok(value) =>
                Ok(value.is_truthy()?),

            Err(_) =>
                Ok(false),
        }
    }


    fn assert_be_documented(
        &self,
        py: Python<'_>,
        message: String,
    ) -> PyResult<Py<Assertion>> {
        if !self._be_documented(py)? {
            return Err(
                PyAssertionError::new_err(message)
            );
        }

        Ok(clone_assertion(py, self)?)
    }


    #[pyo3(signature = (custom_expt = None))]
    fn must_be_documented(
        &self,
        py: Python<'_>,
        custom_expt: Option<Bound<'_, PyType>>,
    ) -> PyResult<()> {
        if !self._be_documented(py)? {
            let exception =
                match custom_expt {
                    Some(value) => value,
                    None =>
                        default_exception_type(
                            py,
                            "TypeError",
                        )?,
                };


            let message = format!(
                "Object {} is not documented",
                self.target.bind(py).repr()?
            );


            return raise_custom(
                exception,
                message,
            );
        }

        Ok(())
    }


    fn should_be_documented(
        &self,
        py: Python<'_>,
    ) -> PyResult<bool> {
        self._be_documented(py)
    }


    // ========================================================
    // ASYNC RETURN
    // ========================================================

    fn _return_async<'py>(
        &self,
        py: Python<'py>,
        return_type: Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                return_type.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_return_async",
            args,
        )
    }


    fn assert_async_return<'py>(
        &self,
        py: Python<'py>,
        message: String,
        return_type: Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let self_obj: Py<Assertion> =
            clone_assertion(py, self)?;


        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                return_type.as_any(),
                message.into_pyobject(py)?.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_assert_async_return",
            args,
        )
    }


    #[pyo3(signature = (return_type, custom_expt = None))]
    fn must_async_return<'py>(
        &self,
        py: Python<'py>,
        return_type: Bound<'py, PyAny>,
        custom_expt: Option<Bound<'py, PyType>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let custom =
            match custom_expt {
                Some(value) => value,
                None =>
                    default_exception_type(
                        py,
                        "TypeError",
                    )?,
            };


        let message = format!(
            "Object async {} does not return {}",
            self.target.bind(py).repr()?,
            return_type.repr()?
        );


        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                return_type.as_any(),
                custom.as_any(),
                message.into_pyobject(py)?.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_must_async_return",
            args,
        )
    }


    fn should_async_return<'py>(
        &self,
        py: Python<'py>,
        return_type: Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        self._return_async(
            py,
            return_type,
        )
    }


    // ========================================================
    // ASYNC RAISE
    // ========================================================

    fn _raise_async<'py>(
        &self,
        py: Python<'py>,
        exception: Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                exception.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_raise_async",
            args,
        )
    }


    fn assert_async_raise<'py>(
        &self,
        py: Python<'py>,
        message: String,
        exception: Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let self_obj: Py<Assertion> =
            clone_assertion(py, self)?;


        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                exception.as_any(),
                message.into_pyobject(py)?.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_assert_async_raise",
            args,
        )
    }


    #[pyo3(signature = (exception, custom_expt = None))]
    fn must_async_raise<'py>(
        &self,
        py: Python<'py>,
        exception: Bound<'py, PyAny>,
        custom_expt: Option<Bound<'py, PyType>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let custom =
            match custom_expt {
                Some(value) => value,
                None =>
                    default_exception_type(
                        py,
                        "TypeError",
                    )?,
            };


        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                exception.as_any(),
                custom.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_must_async_raise",
            args,
        )
    }


    fn should_async_raise<'py>(
        &self,
        py: Python<'py>,
        exception: Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        self._raise_async(
            py,
            exception,
        )
    }


    // ========================================================
    // RUN WITHIN
    // ========================================================

    fn _be_run_within<'py>(
        &self,
        py: Python<'py>,
        time_limit: f64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                time_limit.into_pyobject(py)?.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_be_async_run_within",
            args,
        )
    }


    fn assert_be_run_within<'py>(
        &self,
        py: Python<'py>,
        message: String,
        time_limit: f64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let self_obj: Py<Assertion> =
            clone_assertion(py, self)?;


        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                time_limit.into_pyobject(py)?.as_any(),
                message.into_pyobject(py)?.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_assert_async_run_within",
            args,
        )
    }


    #[pyo3(signature = (time_limit, custom_expt = None))]
    fn must_be_run_within<'py>(
        &self,
        py: Python<'py>,
        time_limit: f64,
        custom_expt: Option<Bound<'py, PyType>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let custom =
            match custom_expt {
                Some(value) => value,
                None =>
                    default_exception_type(
                        py,
                        "TimeoutError",
                    )?,
            };


        let message = format!(
            "Object {} did not execute in less than {} seconds",
            self.target.bind(py).repr()?,
            time_limit
        );


        let args = PyTuple::new(
            py,
            [
                self.target.bind(py).as_any(),
                self.args.bind(py).as_any(),
                self.kwargs.bind(py).as_any(),
                self.async_fn.into_pyobject(py)?.as_any(),
                time_limit.into_pyobject(py)?.as_any(),
                custom.as_any(),
                message.into_pyobject(py)?.as_any(),
            ],
        )?;

        async_helper_call(
            py,
            "_must_async_run_within",
            args,
        )
    }


    fn should_be_run_within<'py>(
        &self,
        py: Python<'py>,
        time_limit: f64,
    ) -> PyResult<Bound<'py, PyAny>> {
        self._be_run_within(
            py,
            time_limit,
        )
    }
}


// ============================================================
// Free functions
// ============================================================

#[pyfunction]
fn classname(
    obj: Bound<'_, PyAny>,
) -> PyResult<String> {
    classname_bound(&obj)
}


#[pyfunction]
fn structure(
    obj: Bound<'_, PyAny>,
) -> PyResult<Bound<'_, PyAny>> {
    obj.getattr("__dict__")
}


// ============================================================
// Python module
// ============================================================

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Assertion>()?;
    m.add_function(wrap_pyfunction!(classname, m)?)?;
    m.add_function(wrap_pyfunction!(structure, m)?)?;

    Ok(())
}
