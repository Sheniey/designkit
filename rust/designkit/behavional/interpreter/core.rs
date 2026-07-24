
pub trait Expression {
    type Output;

    fn interpret(&self) -> Self::Output;
}

pub struct ExpressionUnit<T> {
    value: T,
}

impl<T: Clone> Expression for ExpressionUnit<T> {
    type Output = T;

    fn new(value: T) -> Self {
        ExpressionUnit { value }
    }

    fn __repr__(&self) -> String {
        format!("{:?}({:?})", self.class.name, self.value)
    }

    fn condition(&self) -> bool {
        true
    }

    fn interpret(&self) -> T {
        self.value.clone()
    }
}
