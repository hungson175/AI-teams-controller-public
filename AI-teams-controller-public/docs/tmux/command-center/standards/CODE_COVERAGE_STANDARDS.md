# Code Coverage Standards for AI Teams Controller

**Created:** 2026-01-04
**Author:** TL (Tech Lead)
**Status:** APPROVED

---

## Standards

| Component | Minimum Coverage | Target |
|-----------|------------------|--------|
| **Frontend (Next.js)** | 70% | 75-80% |
| **Backend (FastAPI)** | 80% | 85-90% |

---

## Justification

### Why Frontend at 70%

1. **UI code complexity** - Presentation logic is harder to unit test
2. **Integration tests preferred** - Kent C. Dodds: "Write tests. Not too many. Mostly integration."
3. **Server Components** - Next.js Server Components are difficult to unit test
4. **Industry alignment** - Google considers 75% "commendable"

### Why Backend at 80%

1. **API logic is deterministic** - Easier to test than UI
2. **Business logic criticality** - Must be thoroughly tested
3. **Python tooling** - pytest makes high coverage achievable
4. **Industry standard** - Microsoft/Google target 80%

---

## Industry Research

### Google Standards
- 60% = Acceptable
- 75% = Commendable
- 90% = Exemplary

### Microsoft Standards
- 70-80% = Optimal
- Azure DevOps defaults to 70%

### TDD Expert Consensus
- 80-90% is the practical sweet spot
- Diminishing returns above 80%
- Last 20% takes 90% of effort

---

## Coverage by Code Type

### Backend Breakdown

| Code Type | Target Coverage |
|-----------|-----------------|
| Business logic | 90-95% |
| API endpoints | 85-90% |
| Integration points | 80-90% |
| Utilities/helpers | 70-80% |

### Frontend Breakdown

| Code Type | Target Coverage |
|-----------|-----------------|
| Business logic/hooks | 80-85% |
| API integration | 75-80% |
| UI components | 65-75% |
| Utilities | 70-80% |

---

## Enforcement

### Frontend (Jest)

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  }
}
```

### Backend (pytest)

```ini
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=app --cov-fail-under=80"
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Frontend tests with coverage
  run: cd frontend && pnpm test --coverage

- name: Backend tests with coverage
  run: cd backend && uv run pytest --cov=app --cov-fail-under=80
```

---

## Anti-Patterns to Avoid

1. **Gaming metrics** - Writing trivial tests just to hit percentages
2. **Testing getters/setters** - Skip trivial code
3. **100% obsession** - Severe diminishing returns
4. **Coverage without quality** - Coverage measures execution, not correctness

---

## TL Spec Requirement

**All TL specs MUST include coverage requirements:**

```markdown
## Test Coverage Requirements
- Frontend: 70% minimum (specific components: X%)
- Backend: 80% minimum (business logic: 90%)
```

---

## Sources

- [Google Testing Blog: Code Coverage Best Practices](https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)
- [Martin Fowler: Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
- [Kent C. Dodds: How to know what to test](https://kentcdodds.com/blog/how-to-know-what-to-test)
- [Microsoft Learn: Unit Testing Code Coverage](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-code-coverage)
- [Bullseye: Minimum Acceptable Code Coverage](https://www.bullseye.com/minimum.html)
- [FastAPI Official: Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Next.js Official: Testing](https://nextjs.org/docs/app/guides/testing)
