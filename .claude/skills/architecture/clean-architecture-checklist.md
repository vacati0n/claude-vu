# Skill: Architecture Foundations

## Purpose
Provide reusable architecture guidance for designing maintainable, modular, and scalable systems.

## Principles
- Business rules remain independent from infrastructure.
- Dependency flow points from outer layers to inner abstractions.
- Boundaries are explicit and enforced by module structure.
- Integration concerns are isolated through adapters.

## Best Practices
- Model use cases in an application layer with clear inputs and outputs.
- Keep domain models pure and free of framework coupling.
- Define interface contracts at boundaries and implement adapters externally.
- Record architecture decisions when tradeoffs are significant.

## Anti-patterns
- Treating controllers as business-logic containers.
- Leaking persistence models into domain logic.
- Sharing utility modules that hide cross-layer dependencies.

## Examples
```csharp
public interface IOrderRepository
{
	Task<Order?> GetByIdAsync(Guid id, CancellationToken ct);
	Task SaveAsync(Order order, CancellationToken ct);
}

public sealed class PlaceOrderUseCase
{
	private readonly IOrderRepository _orders;
	public PlaceOrderUseCase(IOrderRepository orders) => _orders = orders;
}
```

## Decision Rules
- Introduce a new layer only when it reduces coupling or clarifies ownership.
- Prefer composition over inheritance across architectural boundaries.
- Reject designs that require inward layers to know infrastructure details.

## Common Mistakes
- Creating abstractions without real variation points.
- Mixing orchestration logic with domain invariants.
- Delaying architecture decisions until integration failures occur.
