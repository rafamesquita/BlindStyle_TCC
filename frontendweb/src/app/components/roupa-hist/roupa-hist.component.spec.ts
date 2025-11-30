import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoupaHistComponent } from './roupa-hist.component';

describe('RoupaHistComponent', () => {
  let component: RoupaHistComponent;
  let fixture: ComponentFixture<RoupaHistComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoupaHistComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoupaHistComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
