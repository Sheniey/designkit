use pyo3::prelude::*;
pub mod behavioral;

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let behavioral = PyModule::new(m.py(), "behavioral")?;

    behavioral::register(&behavioral)?;

    m.add_submodule(&behavioral)?;

    Ok(())
}
